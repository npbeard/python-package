import importlib
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SRC = ROOT / "src"

for path in (SRC, ROOT):
    if path.exists():
        sys.path.insert(0, str(path))

echochamber = importlib.import_module("echochamber")
Persona = echochamber.Persona
NoirVoice = echochamber.NoirVoice
EngineConfig = echochamber.EngineConfig


def test_persona_call_magic_method():
    p = Persona(
        name="Spade",
        voice=NoirVoice(),
        config=EngineConfig(include_time=False, chaos=False),
    )
    res = p("hello", layers=1)  # __call__
    assert res.original == "hello"
    assert "The city never sleeps" in res.transformed


def test_generator_echo_chunks():
    p = Persona(
        name="Spade",
        voice=NoirVoice(),
        config=EngineConfig(include_time=False, chaos=False),
    )
    chunks = list(p.echo("hello world", chunk_size=5))
    assert "".join(chunks) == (
        p.echo_once("hello world")["result"].transformed
    )
