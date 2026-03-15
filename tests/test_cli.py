from pathlib import Path

import pytest

from echochamber.cli import (
    _env_non_negative_int,
    _make_voice,
    _prompt_non_negative_int,
    _read_text_from_path,
    _resolve_input_text,
    build_parser,
)
from echochamber.voices import NoirVoice, SciFiVoice, TherapyVoice


@pytest.mark.parametrize(
    ("name", "expected_type"),
    [
        ("noir", NoirVoice),
        ("scifi", SciFiVoice),
        ("sci-fi", SciFiVoice),
        ("sci_fi", SciFiVoice),
        ("therapy", TherapyVoice),
        ("therapist", TherapyVoice),
    ],
)
def test_make_voice_supports_aliases(name, expected_type):
    assert isinstance(_make_voice(name), expected_type)


def test_make_voice_rejects_unknown_name():
    with pytest.raises(SystemExit, match="Unknown voice"):
        _make_voice("mystery")


def test_parser_rejects_negative_numbers():
    parser = build_parser()
    with pytest.raises(SystemExit):
        parser.parse_args(["hello", "--layers", "-1"])


def test_read_text_from_path_reads_utf8_file(tmp_path: Path):
    sample = tmp_path / "sample.txt"
    sample.write_text("hello from file\n", encoding="utf-8")
    assert _read_text_from_path(sample) == "hello from file"


def test_read_text_from_path_rejects_missing_file(tmp_path: Path):
    missing = tmp_path / "missing.txt"
    with pytest.raises(SystemExit, match="Input file not found"):
        _read_text_from_path(missing)


def test_resolve_input_text_uses_positional_text():
    parser = build_parser()
    assert _resolve_input_text(parser, "hello", None) == "hello"


def test_resolve_input_text_uses_path_input(tmp_path: Path):
    parser = build_parser()
    sample = tmp_path / "sample.txt"
    sample.write_text("hello path", encoding="utf-8")
    assert _resolve_input_text(parser, None, sample) == "hello path"


def test_resolve_input_text_rejects_both_text_sources(tmp_path: Path):
    parser = build_parser()
    sample = tmp_path / "sample.txt"
    sample.write_text("hello path", encoding="utf-8")
    with pytest.raises(SystemExit):
        _resolve_input_text(parser, "hello", sample)


def test_prompt_non_negative_int_retries_until_valid(monkeypatch):
    answers = iter(["abc", "-2", "5"])
    monkeypatch.setattr("builtins.input", lambda _: next(answers))
    assert _prompt_non_negative_int("Layers", 1) == 5


def test_prompt_non_negative_int_accepts_default(monkeypatch):
    monkeypatch.setattr("builtins.input", lambda _: "")
    assert _prompt_non_negative_int("Layers", 3) == 3


def test_env_non_negative_int_returns_default_when_unset(monkeypatch):
    monkeypatch.delenv("ECHOCHAMBER_DEFAULT_LAYERS", raising=False)
    assert _env_non_negative_int("ECHOCHAMBER_DEFAULT_LAYERS", 3) == 3


def test_env_non_negative_int_rejects_invalid_value(monkeypatch):
    monkeypatch.setenv("ECHOCHAMBER_DEFAULT_LAYERS", "abc")
    with pytest.raises(SystemExit, match="must be an integer"):
        _env_non_negative_int("ECHOCHAMBER_DEFAULT_LAYERS", 1)


def test_env_non_negative_int_rejects_negative_value(monkeypatch):
    monkeypatch.setenv("ECHOCHAMBER_DEFAULT_LAYERS", "-2")
    with pytest.raises(SystemExit, match="must be non-negative"):
        _env_non_negative_int("ECHOCHAMBER_DEFAULT_LAYERS", 1)


def test_parser_supports_conversation_mode_arguments():
    parser = build_parser()
    args = parser.parse_args(
        [
            "--conversation",
            "--topic",
            "Class project ideas",
            "--rounds",
            "2",
            "--participants",
            "noir,scifi",
        ]
    )
    assert args.conversation is True
    assert args.topic == "Class project ideas"
    assert args.rounds == 2
    assert args.participants == "noir,scifi"
