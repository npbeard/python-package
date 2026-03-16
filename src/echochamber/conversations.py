from __future__ import annotations

from collections import Counter
from dataclasses import dataclass, field
from datetime import datetime
import json
from pathlib import Path
import re
from typing import Iterable, Iterator

from .personas import Persona
from .utils import deep_copy, now_string, shallow_copy
from .voices import NoirVoice, SciFiVoice, TherapyVoice, Voice


_WORD_RE = re.compile(r"[A-Za-z']+")
_VOICE_TYPES: dict[str, type[Voice]] = {
    "noir": NoirVoice,
    "scifi": SciFiVoice,
    "therapy": TherapyVoice,
}


@dataclass(frozen=True, slots=True)
class Message:
    """Immutable conversation event stored in a transcript."""

    speaker: str
    content: str
    timestamp: str
    mood: str = "neutral"
    tags: tuple[str, ...] = ()


@dataclass(frozen=True, slots=True)
class ConversationConfig:
    """Hashable settings object for multi-persona simulations."""

    max_rounds: int = 3
    replay_chunk_size: int = 60
    memory_window: int = 2
    summary_word_count: int = 5


@dataclass(slots=True)
class MemoryBank:
    """Mutable memory store that keeps a lightweight transcript by speaker."""

    entries: dict[str, list[str]] = field(default_factory=dict)

    def remember(self, speaker: str, text: str) -> None:
        self.entries.setdefault(speaker, []).append(text)

    def recall(self, speaker: str, *, limit: int = 2) -> list[str]:
        return self.entries.get(speaker, [])[-limit:]

    def snapshot(self) -> dict[str, list[str]]:
        return {speaker: items[:] for speaker, items in self.entries.items()}


@dataclass(slots=True)
class Conversation:
    """
    Multi-persona conversation simulator.

    Demonstrates composition, collections, magic methods, persistence,
    iterables, and mutable vs immutable state.
    """

    title: str
    participants: dict[str, Persona] = field(default_factory=dict)
    history: list[Message] = field(default_factory=list)
    memory: MemoryBank = field(default_factory=MemoryBank)
    config: ConversationConfig = field(default_factory=ConversationConfig)

    default_rounds: int = 3

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        if not self.title:
            raise ValueError("Conversation title cannot be empty.")

    def __len__(self) -> int:
        return len(self.history)

    def __iter__(self) -> Iterator[Message]:
        return iter(self.history)

    def __contains__(self, item: object) -> bool:
        if isinstance(item, str):
            return item in self.participants
        return item in self.history

    def __repr__(self) -> str:
        return (
            f"Conversation(title={self.title!r}, "
            f"participants={list(self.participants)!r}, "
            f"messages={len(self.history)})"
        )

    @property
    def participant_names(self) -> list[str]:
        return list(self.participants)

    def add_personas(self, *personas: Persona) -> None:
        for persona in personas:
            self.participants[persona.name] = persona

    def post_message(
        self,
        speaker: str,
        text: str,
        *,
        mood: str = "neutral",
        tags: Iterable[str] = (),
    ) -> Message:
        if speaker not in self.participants:
            raise ValueError(f"Unknown participant: {speaker}")
        message = Message(
            speaker=speaker,
            content=text,
            timestamp=now_string(),
            mood=mood,
            tags=tuple(tags),
        )
        self.history.append(message)
        self.memory.remember(speaker, text)
        return message

    def _build_prompt(self, speaker: str, topic: str, round_number: int) -> str:
        recent_lines = [
            f"{msg.speaker}: {msg.content}"
            for msg in self.history[-self.config.memory_window :]
        ]
        remembered = self.memory.recall(speaker, limit=self.config.memory_window)
        memory_text = " | ".join(remembered) if remembered else "No prior memory."
        recent_text = " | ".join(recent_lines) if recent_lines else "Conversation just started."
        return (
            f"Topic: {topic}. Round: {round_number}. "
            f"Recent: {recent_text}. Memory: {memory_text}."
        )

    def generate_reply(
        self,
        speaker: str,
        topic: str,
        *,
        round_number: int,
        layers: int = 1,
        intensity: int = 1,
    ) -> Message:
        persona = self.participants[speaker]
        prompt = self._build_prompt(speaker, topic, round_number)
        result = persona.echo_once(prompt, layers=layers, intensity=intensity)
        tags = [persona.voice.registry_name, "generated", f"round-{round_number}"]
        if persona.config.chaos:
            tags.append("regex")
        if persona.config.include_time:
            tags.append("datetime")
        mood = "chaotic" if persona.config.chaos else "focused"
        return self.post_message(
            speaker,
            result["result"].transformed,
            mood=mood,
            tags=tags,
        )

    def simulate(
        self,
        topic: str,
        *,
        rounds: int | None = None,
        layers: int = 1,
        intensity: int = 1,
    ) -> list[Message]:
        if not self.participants:
            raise ValueError("Add at least one persona before simulating.")

        total_rounds = self.default_rounds if rounds is None else rounds
        total_rounds = min(total_rounds, self.config.max_rounds)
        generated: list[Message] = []
        for round_number in range(1, total_rounds + 1):
            for speaker in self.participant_names:
                generated.append(
                    self.generate_reply(
                        speaker,
                        topic,
                        round_number=round_number,
                        layers=layers,
                        intensity=intensity,
                    )
                )
        return generated

    def replay(self, *, chunk_size: int | None = None) -> Iterable[str]:
        size = self.config.replay_chunk_size if chunk_size is None else chunk_size
        if size <= 0:
            raise ValueError("chunk_size must be positive.")

        transcript = "\n".join(
            f"[{msg.timestamp}] {msg.speaker} ({msg.mood}): {msg.content}"
            for msg in self.history
        )
        for index in range(0, len(transcript), size):
            yield transcript[index : index + size]

    def summary_stats(self) -> dict[str, object]:
        by_speaker = Counter(msg.speaker for msg in self.history)
        all_words = Counter(
            word.lower()
            for msg in self.history
            for word in _WORD_RE.findall(msg.content)
            if len(word) > 3
        )
        return {
            "title": self.title,
            "participants": self.participant_names,
            "message_count": len(self.history),
            "messages_by_speaker": dict(by_speaker),
            "top_words": all_words.most_common(self.config.summary_word_count),
        }

    def clone_shallow(self) -> Conversation:
        return shallow_copy(self)

    def clone_deep(self) -> Conversation:
        return deep_copy(self)

    def to_dict(self) -> dict[str, object]:
        return {
            "title": self.title,
            "participants": [
                {
                    "name": persona.name,
                    "voice": persona.voice.registry_name,
                    "tags": persona.tags[:],
                    "config": {
                        "include_time": persona.config.include_time,
                        "time_format": persona.config.time_format,
                        "chaos": persona.config.chaos,
                    },
                }
                for persona in self.participants.values()
            ],
            "history": [
                {
                    "speaker": msg.speaker,
                    "content": msg.content,
                    "timestamp": msg.timestamp,
                    "mood": msg.mood,
                    "tags": list(msg.tags),
                }
                for msg in self.history
            ],
            "stats": self.summary_stats(),
        }

    def save(self, path: Path) -> Path:
        path.write_text(json.dumps(self.to_dict(), indent=2), encoding="utf-8")
        return path

    @classmethod
    def load(cls, path: Path) -> Conversation:
        payload = json.loads(path.read_text(encoding="utf-8"))
        conversation = cls(title=payload["title"])
        for item in payload["participants"]:
            voice_name = str(item["voice"])
            voice_cls = _VOICE_TYPES[voice_name]
            config_payload = item["config"]
            from .utils import EngineConfig

            persona = Persona(
                name=str(item["name"]),
                voice=voice_cls(),
                tags=list(item.get("tags", [])),
                config=EngineConfig(
                    include_time=bool(config_payload["include_time"]),
                    time_format=str(config_payload["time_format"]),
                    chaos=bool(config_payload["chaos"]),
                ),
            )
            conversation.add_personas(persona)

        for item in payload["history"]:
            message = Message(
                speaker=str(item["speaker"]),
                content=str(item["content"]),
                timestamp=str(item["timestamp"]),
                mood=str(item.get("mood", "neutral")),
                tags=tuple(item.get("tags", [])),
            )
            conversation.history.append(message)
            conversation.memory.remember(message.speaker, message.content)
        return conversation
