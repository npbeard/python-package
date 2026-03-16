import pytest

from echochamber import Persona, NoirVoice
from echochamber.utils import EngineConfig


def test_persona_call_magic_method():
    p = Persona(
        name="Spade",
        voice=NoirVoice(),
        config=EngineConfig(include_time=False, chaos=False)
    )
    res = p("hello", layers=1)  # __call__
    assert res.original == "hello"
    assert "The city never sleeps" in res.transformed


def test_generator_echo_chunks():
    p = Persona(
        name="Spade",
        voice=NoirVoice(),
        config=EngineConfig(include_time=False, chaos=False)
    )
    chunks = list(p.echo("hello world", chunk_size=5))
    assert "".join(chunks) == p.echo_once("hello world")["result"].transformed


def test_persona_repr():
    p = Persona(name="Spade", voice=NoirVoice(), config=EngineConfig(include_time=False))
    r = repr(p)
    assert "Spade" in r
    assert "noir" in r


def test_persona_iter_over_tags():
    p = Persona(name="Spade", voice=NoirVoice())
    p.add_tags("cli", "test")
    assert list(p) == ["cli", "test"]


def test_add_tags_no_duplicates():
    p = Persona(name="Spade", voice=NoirVoice())
    p.add_tags("a", "a", "b")
    assert p.tags == ["a", "b"]


def test_persona_empty_name_raises():
    with pytest.raises(ValueError):
        Persona(name="", voice=NoirVoice())


def test_persona_whitespace_name_raises():
    with pytest.raises(ValueError):
        Persona(name="   ", voice=NoirVoice())


def test_echo_rejects_non_positive_chunk_size():
    p = Persona(name="Spade", voice=NoirVoice())
    with pytest.raises(ValueError, match="chunk_size"):
        list(p.echo("hello", chunk_size=0))


def test_echo_once_rejects_negative_layers():
    p = Persona(name="Spade", voice=NoirVoice())
    with pytest.raises(ValueError, match="layers"):
        p.echo_once("hello", layers=-1)


def test_echo_once_rejects_negative_intensity_when_chaos_enabled():
    p = Persona(
        name="Spade",
        voice=NoirVoice(),
        config=EngineConfig(include_time=False, chaos=True),
    )
    with pytest.raises(ValueError, match="intensity"):
        p.echo_once("hello", intensity=-1)


def test_scifi_voice():
    from echochamber import SciFiVoice
    v = SciFiVoice()
    assert "signal acquired" in v.transform("hello")


def test_therapy_voice():
    from echochamber import TherapyVoice
    v = TherapyVoice()
    assert v.transform("hello").startswith("I hear you")
