"""
Tests for echochamber.api  (the optional FastAPI application)
--------------------------------------------------------------
Uses FastAPI's built-in TestClient (via httpx) so no live server is needed.

Endpoints exercised:
  POST   /sessions                          – body parameters  (create session)
  GET    /sessions/{session_id}             – path parameter   (get session)
  GET    /sessions/{session_id}?include_stats=false – query parameter
  POST   /sessions/{session_id}/messages   – path + body      (add message)
  POST   /sessions/{session_id}/simulate   – path + query + body (simulate)

Error cases:
  • 404 when session_id does not exist
  • 500 when an unknown speaker is posted (ValueError from Conversation)

Requires the [api] optional dependencies:
  pip install echochamber[api]   or   pip install fastapi httpx
"""

from __future__ import annotations

import pytest

# Skip the entire module if FastAPI / httpx are not installed.
pytest.importorskip("fastapi", reason="fastapi not installed; skipping API tests")
pytest.importorskip("httpx", reason="httpx not installed; skipping API tests")

from fastapi.testclient import TestClient  # noqa: E402  (after importorskip)

from echochamber import create_app  # noqa: E402


# ---------------------------------------------------------------------------
# Shared fixtures
# ---------------------------------------------------------------------------

@pytest.fixture(scope="module")
def client() -> TestClient:
    """One TestClient for the whole module — avoids recreating the app."""
    app = create_app()
    # raise_server_exceptions=False lets us assert on 4xx/5xx status codes
    # without the TestClient re-raising the underlying Python exception.
    return TestClient(app, raise_server_exceptions=False)


@pytest.fixture()
def noir_session(client: TestClient) -> str:
    """
    Helper fixture: creates a fresh session with a single Noir persona
    and returns its session_id.  Used by several tests below.
    """
    response = client.post(
        "/sessions",
        json={
            "title": "Fixture session",
            "personas": [
                {
                    "name": "Spade",
                    "voice": "noir",
                    "include_time": False,
                    "chaos": False,
                }
            ],
        },
    )
    assert response.status_code == 200
    return response.json()["session_id"]


# ---------------------------------------------------------------------------
# POST /sessions  — body parameters
# ---------------------------------------------------------------------------

class TestCreateSession:
    """
    POST /sessions accepts a JSON body (body parameter) and returns
    a UUID session_id together with the list of participant names.
    """

    def test_create_session_returns_200(self, client: TestClient):
        response = client.post(
            "/sessions",
            json={"title": "Hello world", "personas": []},
        )
        assert response.status_code == 200

    def test_create_session_returns_session_id(self, client: TestClient):
        response = client.post("/sessions", json={"title": "T"})
        data = response.json()
        assert "session_id" in data
        assert isinstance(data["session_id"], str)
        assert len(data["session_id"]) > 0

    def test_create_session_with_single_persona(self, client: TestClient):
        response = client.post(
            "/sessions",
            json={
                "title": "Solo",
                "personas": [{"name": "Nova", "voice": "scifi", "include_time": False}],
            },
        )
        assert response.status_code == 200
        assert response.json()["participants"] == ["Nova"]

    def test_create_session_with_multiple_personas(self, client: TestClient):
        response = client.post(
            "/sessions",
            json={
                "title": "Multi",
                "personas": [
                    {"name": "Spade", "voice": "noir"},
                    {"name": "Nova", "voice": "scifi"},
                    {"name": "Doc", "voice": "therapy"},
                ],
            },
        )
        assert response.status_code == 200
        participants = response.json()["participants"]
        assert set(participants) == {"Spade", "Nova", "Doc"}

    def test_create_session_no_personas_returns_empty_participants(self, client: TestClient):
        response = client.post("/sessions", json={"title": "Empty"})
        assert response.json()["participants"] == []

    def test_create_session_different_ids_each_time(self, client: TestClient):
        """Each call must produce a unique session_id (UUID-based)."""
        id1 = client.post("/sessions", json={"title": "A"}).json()["session_id"]
        id2 = client.post("/sessions", json={"title": "B"}).json()["session_id"]
        assert id1 != id2

    def test_create_session_invalid_voice_returns_500(self, client: TestClient):
        """
        Passing an unknown voice name causes a KeyError inside _make_persona.
        The current implementation does not catch this, so the server returns 500.
        This test documents the known behaviour (not a test that it's correct).
        """
        response = client.post(
            "/sessions",
            json={"title": "Bad", "personas": [{"name": "X", "voice": "unknown_voice"}]},
        )
        assert response.status_code == 500


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}  — path parameter
# ---------------------------------------------------------------------------

class TestGetSession:
    """
    GET /sessions/{session_id} uses a *path parameter* to identify the session.
    """

    def test_get_existing_session_returns_200(self, client: TestClient, noir_session: str):
        response = client.get(f"/sessions/{noir_session}")
        assert response.status_code == 200

    def test_get_session_response_contains_expected_keys(self, client: TestClient, noir_session: str):
        data = client.get(f"/sessions/{noir_session}").json()
        assert "title" in data
        assert "participants" in data
        assert "history" in data
        assert "stats" in data  # include_stats defaults to True

    def test_get_nonexistent_session_returns_404(self, client: TestClient):
        """Path parameter: a session_id that was never created must return 404."""
        response = client.get("/sessions/this-id-does-not-exist")
        assert response.status_code == 404

    def test_get_session_404_detail_message(self, client: TestClient):
        response = client.get("/sessions/ghost")
        assert "session not found" in response.json()["detail"]


# ---------------------------------------------------------------------------
# GET /sessions/{session_id}?include_stats=false  — query parameter
# ---------------------------------------------------------------------------

class TestGetSessionQueryParam:
    """
    The include_stats *query parameter* controls whether the stats block
    is included in the response payload.
    """

    def test_include_stats_true_by_default(self, client: TestClient, noir_session: str):
        data = client.get(f"/sessions/{noir_session}").json()
        assert "stats" in data

    def test_include_stats_false_omits_stats(self, client: TestClient, noir_session: str):
        """Query parameter: ?include_stats=false strips the stats key."""
        data = client.get(f"/sessions/{noir_session}?include_stats=false").json()
        assert "stats" not in data

    def test_include_stats_false_still_has_history(self, client: TestClient, noir_session: str):
        data = client.get(f"/sessions/{noir_session}?include_stats=false").json()
        assert "history" in data


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/messages  — path + body parameters
# ---------------------------------------------------------------------------

class TestAddMessage:
    """
    POST /sessions/{session_id}/messages uses a path parameter (session_id)
    and a JSON body parameter (speaker, text, mood, tags).
    """

    def test_add_message_returns_200(self, client: TestClient, noir_session: str):
        response = client.post(
            f"/sessions/{noir_session}/messages",
            json={"speaker": "Spade", "text": "It was a quiet evening."},
        )
        assert response.status_code == 200

    def test_add_message_response_contains_speaker_and_timestamp(
        self, client: TestClient, noir_session: str
    ):
        response = client.post(
            f"/sessions/{noir_session}/messages",
            json={"speaker": "Spade", "text": "Something stirred in the dark."},
        )
        data = response.json()
        assert data["speaker"] == "Spade"
        assert "timestamp" in data
        assert isinstance(data["timestamp"], str)

    def test_add_message_with_mood(self, client: TestClient, noir_session: str):
        """Body parameter: optional mood field is accepted without error."""
        response = client.post(
            f"/sessions/{noir_session}/messages",
            json={"speaker": "Spade", "text": "Suspicious.", "mood": "tense"},
        )
        assert response.status_code == 200

    def test_add_message_to_missing_session_returns_404(self, client: TestClient):
        """Path parameter: non-existent session_id must return 404."""
        response = client.post(
            "/sessions/does-not-exist/messages",
            json={"speaker": "X", "text": "Hello"},
        )
        assert response.status_code == 404

    def test_add_message_unknown_speaker_returns_500(self, client: TestClient, noir_session: str):
        """
        Posting a speaker name that is not a registered persona raises
        ValueError inside Conversation.post_message.  Documents current behaviour.
        """
        response = client.post(
            f"/sessions/{noir_session}/messages",
            json={"speaker": "NotAParticipant", "text": "Ghost message"},
        )
        assert response.status_code == 500

    def test_message_appears_in_session_history(self, client: TestClient):
        """End-to-end: create session → post message → verify it shows in GET."""
        # Create a fresh session
        sid = client.post(
            "/sessions",
            json={
                "title": "History check",
                "personas": [{"name": "Spade", "voice": "noir", "include_time": False}],
            },
        ).json()["session_id"]

        # Post one message
        client.post(
            f"/sessions/{sid}/messages",
            json={"speaker": "Spade", "text": "The fog rolled in."},
        )

        # Verify the message appears in the session history
        history = client.get(f"/sessions/{sid}").json()["history"]
        assert len(history) == 1
        assert history[0]["speaker"] == "Spade"
        assert "The fog rolled in." in history[0]["content"]


# ---------------------------------------------------------------------------
# POST /sessions/{session_id}/simulate  — path + query + body parameters
# ---------------------------------------------------------------------------

class TestSimulateSession:
    """
    POST /sessions/{session_id}/simulate uses:
    - path parameter:  session_id
    - query parameters: rounds, layers, intensity
    - body parameter:  optional topic
    """

    def test_simulate_returns_200(self, client: TestClient, noir_session: str):
        response = client.post(
            f"/sessions/{noir_session}/simulate",
            params={"rounds": 1},
            json={},
        )
        assert response.status_code == 200

    def test_simulate_response_contains_generated_messages_and_stats(
        self, client: TestClient, noir_session: str
    ):
        response = client.post(
            f"/sessions/{noir_session}/simulate",
            params={"rounds": 1},
            json={"topic": "The case begins."},
        )
        data = response.json()
        assert "generated_messages" in data
        assert "stats" in data

    def test_simulate_rounds_query_parameter(self, client: TestClient):
        """
        Query parameter: rounds controls how many messages are generated.
        With 1 persona and rounds=2, we expect 2 generated messages.
        """
        sid = client.post(
            "/sessions",
            json={
                "title": "Rounds test",
                "personas": [{"name": "Spade", "voice": "noir", "include_time": False}],
            },
        ).json()["session_id"]

        data = client.post(
            f"/sessions/{sid}/simulate",
            params={"rounds": 2},
            json={"topic": "Crime scene"},
        ).json()

        assert data["generated_messages"] == 2

    def test_simulate_with_topic_body_parameter(self, client: TestClient):
        """Body parameter: topic is passed in the JSON body."""
        sid = client.post(
            "/sessions",
            json={
                "title": "Topic body test",
                "personas": [{"name": "Doc", "voice": "therapy", "include_time": False}],
            },
        ).json()["session_id"]

        response = client.post(
            f"/sessions/{sid}/simulate",
            params={"rounds": 1},
            json={"topic": "Finding inner peace"},
        )
        assert response.status_code == 200

    def test_simulate_missing_session_returns_404(self, client: TestClient):
        """Path parameter: simulate on a non-existent session must return 404."""
        response = client.post(
            "/sessions/ghost-session/simulate",
            params={"rounds": 1},
            json={},
        )
        assert response.status_code == 404

    def test_simulate_stats_message_count_matches_generated(self, client: TestClient):
        """Stats in the response must reflect the total messages after simulation."""
        sid = client.post(
            "/sessions",
            json={
                "title": "Stats check",
                "personas": [{"name": "Nova", "voice": "scifi", "include_time": False}],
            },
        ).json()["session_id"]

        data = client.post(
            f"/sessions/{sid}/simulate",
            params={"rounds": 1},
            json={},
        ).json()

        assert data["stats"]["message_count"] == data["generated_messages"]
