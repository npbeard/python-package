from __future__ import annotations

from dataclasses import dataclass
from typing import Any
from uuid import uuid4

from .conversations import Conversation
from .personas import Persona
from .utils import EngineConfig
from .voices import NoirVoice, SciFiVoice, TherapyVoice


_VOICE_MAP = {
    "noir": NoirVoice,
    "scifi": SciFiVoice,
    "therapy": TherapyVoice,
}


@dataclass(slots=True)
class SessionStore:
    """Small in-memory session store used by the optional FastAPI app."""

    sessions: dict[str, Conversation]


def _make_persona(payload: dict[str, Any]) -> Persona:
    voice_name = str(payload.get("voice", "noir")).strip().lower()
    voice_cls = _VOICE_MAP[voice_name]
    return Persona(
        name=str(payload.get("name", voice_name.title())),
        voice=voice_cls(),
        tags=list(payload.get("tags", [])),
        config=EngineConfig(
            include_time=bool(payload.get("include_time", True)),
            chaos=bool(payload.get("chaos", False)),
        ),
    )


def create_app() -> Any:
    """
    Return a FastAPI application if FastAPI is installed.

    This keeps the package usable without requiring API dependencies.
    """

    try:
        from fastapi import Body, FastAPI, HTTPException
    except ImportError as exc:
        raise RuntimeError(
            "Install the API extra with `pip install echochamber[api]`."
        ) from exc

    app = FastAPI(title="echochamber API", version="0.1.3")
    store = SessionStore(sessions={})

    @app.post("/sessions")
    def create_session(payload: dict[str, Any] = Body(...)) -> dict[str, Any]:
        session_id = str(uuid4())
        conversation = Conversation(title=str(payload.get("title", "Session")))
        personas = [_make_persona(item) for item in payload.get("personas", [])]
        if personas:
            conversation.add_personas(*personas)
        store.sessions[session_id] = conversation
        return {"session_id": session_id, "participants": conversation.participant_names}

    @app.get("/sessions/{session_id}")
    def get_session(
        session_id: str,
        include_stats: bool = True,
    ) -> dict[str, Any]:
        conversation = store.sessions.get(session_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="session not found")
        payload = conversation.to_dict()
        if not include_stats:
            payload.pop("stats", None)
        return payload

    @app.post("/sessions/{session_id}/messages")
    def add_message(
        session_id: str,
        payload: dict[str, Any] = Body(...),
    ) -> dict[str, Any]:
        conversation = store.sessions.get(session_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="session not found")
        message = conversation.post_message(
            str(payload["speaker"]),
            str(payload["text"]),
            mood=str(payload.get("mood", "neutral")),
            tags=payload.get("tags", []),
        )
        return {"speaker": message.speaker, "timestamp": message.timestamp}

    @app.post("/sessions/{session_id}/simulate")
    def simulate_session(
        session_id: str,
        rounds: int = 3,
        layers: int = 1,
        intensity: int = 1,
        payload: dict[str, Any] = Body(default={}),
    ) -> dict[str, Any]:
        conversation = store.sessions.get(session_id)
        if conversation is None:
            raise HTTPException(status_code=404, detail="session not found")
        topic = str(payload.get("topic", conversation.title))
        messages = conversation.simulate(
            topic,
            rounds=rounds,
            layers=layers,
            intensity=intensity,
        )
        return {
            "generated_messages": len(messages),
            "stats": conversation.summary_stats(),
        }

    return app
