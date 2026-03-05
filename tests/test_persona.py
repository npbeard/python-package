from echochamber import Persona, NoirVoice
from echochamber.utils import EngineConfig


def test_persona_call_magic_method():
    p = Persona(name="Spade", voice=NoirVoice(), config=EngineConfig(include_time=False, chaos=False))
    res = p("hello", layers=1)  # __call__
    assert res.original == "hello"
    assert "The city never sleeps" in res.transformed


def test_generator_echo_chunks():
    p = Persona(name="Spade", voice=NoirVoice(), config=EngineConfig(include_time=False, chaos=False))
    chunks = list(p.echo("hello world", chunk_size=5))
    assert "".join(chunks) == p.echo_once("hello world")["result"].transformed