from pathlib import Path

from echochamber import Conversation, NoirVoice, Persona, SciFiVoice
from echochamber.utils import EngineConfig


def _make_persona(name: str, voice: str, *, chaos: bool = False) -> Persona:
    voice_obj = NoirVoice() if voice == "noir" else SciFiVoice()
    return Persona(
        name=name,
        voice=voice_obj,
        config=EngineConfig(include_time=False, chaos=chaos),
    )


def test_conversation_magic_methods_and_add_personas():
    conversation = Conversation(title="Demo")
    spade = _make_persona("Spade", "noir")
    nova = _make_persona("Nova", "scifi")
    conversation.add_personas(spade, nova)

    assert "Spade" in conversation
    assert len(conversation) == 0
    assert conversation.participant_names == ["Spade", "Nova"]
    assert "Conversation(title='Demo'" in repr(conversation)


def test_conversation_simulate_generates_messages():
    conversation = Conversation(title="AI futures")
    conversation.add_personas(
        _make_persona("Spade", "noir"),
        _make_persona("Nova", "scifi", chaos=True),
    )

    generated = conversation.simulate("How will AI change storytelling?", rounds=2)

    assert len(generated) == 4
    assert len(conversation) == 4
    assert generated[0].speaker == "Spade"
    assert generated[-1].speaker == "Nova"


def test_conversation_replay_and_stats():
    conversation = Conversation(title="Planning")
    conversation.add_personas(_make_persona("Spade", "noir"))
    conversation.post_message("Spade", "We need a careful plan.", tags=["manual"])

    chunks = list(conversation.replay(chunk_size=10))
    stats = conversation.summary_stats()

    assert "".join(chunks)
    assert stats["message_count"] == 1
    assert stats["messages_by_speaker"] == {"Spade": 1}


def test_conversation_clone_shallow_vs_deep():
    """
    Verify shallow-copy vs deep-copy semantics for Conversation.

    Shallow copy (copy.copy):
      - Creates a new Conversation object, but nested mutable fields
        (history, memory.entries, participants) are *shared* with the
        original.  Mutating the original's list is therefore visible
        through the shallow clone.

    Deep copy (copy.deepcopy):
      - Recursively duplicates every nested object, so the clone is
        completely independent of the original.
    """
    conversation = Conversation(title="Clones")
    conversation.add_personas(_make_persona("Spade", "noir"))
    conversation.post_message("Spade", "Original line.")

    shallow = conversation.clone_shallow()
    deep = conversation.clone_deep()

    # Sanity-check: both clones start with the same history length.
    assert len(shallow.history) == 1
    assert len(deep.history) == 1

    # Confirm the shallow clone really shares the same list object.
    assert shallow.history is conversation.history, (
        "shallow copy must share the history list with the original"
    )

    # Confirm the deep clone has its own independent list object.
    assert deep.history is not conversation.history, (
        "deep copy must NOT share the history list with the original"
    )

    # Mutate the original by appending a second message.
    conversation.post_message("Spade", "Second line.")

    # Shallow clone sees the new message because it shares the list.
    assert len(shallow.history) == 2, (
        "shallow clone should reflect the appended message (shared list)"
    )

    # Deep clone is unaffected because its list is independent.
    assert len(deep.history) == 1, (
        "deep clone should NOT reflect the appended message (independent list)"
    )


def test_conversation_save_and_load(tmp_path: Path):
    path = tmp_path / "session.json"
    conversation = Conversation(title="Persistence")
    conversation.add_personas(
        _make_persona("Spade", "noir"),
        _make_persona("Nova", "scifi"),
    )
    conversation.simulate("Package design", rounds=1)
    conversation.save(path)

    loaded = Conversation.load(path)

    assert loaded.title == "Persistence"
    assert loaded.participant_names == ["Spade", "Nova"]
    assert len(loaded.history) == len(conversation.history)
