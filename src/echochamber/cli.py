from __future__ import annotations

import argparse
import os
from pathlib import Path
from dotenv import load_dotenv

from .conversations import Conversation
from .personas import Persona
from .voices import Voice, NoirVoice, SciFiVoice, TherapyVoice
from .utils import EngineConfig


VOICE_ALIASES: dict[str, type[Voice]] = {
    "noir": NoirVoice,
    "scifi": SciFiVoice,
    "sci-fi": SciFiVoice,
    "sci_fi": SciFiVoice,
    "therapy": TherapyVoice,
    "therapist": TherapyVoice,
}


def _make_voice(name: str) -> Voice:
    # A small registry keeps CLI labels and implementation classes in one place.
    normalized = name.lower().strip()
    voice_cls = VOICE_ALIASES.get(normalized)
    if voice_cls is None:
        raise SystemExit(f"Unknown voice: {name}. Use noir|scifi|therapy.")
    return voice_cls()


def _non_negative_int(value: str) -> int:
    parsed = int(value)
    if parsed < 0:
        raise argparse.ArgumentTypeError("must be a non-negative integer")
    return parsed


def _env_non_negative_int(name: str, default: int) -> int:
    raw = os.getenv(name)
    if raw is None:
        return default

    try:
        parsed = int(raw)
    except ValueError as exc:
        raise SystemExit(f"{name} must be an integer, got {raw!r}.") from exc

    if parsed < 0:
        raise SystemExit(f"{name} must be non-negative, got {raw!r}.")

    return parsed


def _read_text_from_path(path: Path) -> str:
    """
    Read UTF-8 text from a filesystem path.
    This gives the project an explicit pathlib-based example.
    """
    try:
        return path.read_text(encoding="utf-8").strip()
    except FileNotFoundError as exc:
        raise SystemExit(f"Input file not found: {path}") from exc
    except OSError as exc:
        raise SystemExit(f"Could not read input file {path}: {exc}") from exc


def _resolve_input_text(
    parser: argparse.ArgumentParser,
    text: str | None,
    input_file: Path | None,
) -> str:
    # Centralizing input resolution keeps main() small and testable.
    if text and input_file:
        parser.error("pass either text or --input-file, not both")
    if input_file is not None:
        content = _read_text_from_path(input_file)
        if not content:
            parser.error("--input-file must not be empty")
        return content
    if text:
        return text
    parser.error("text or --input-file is required unless --interactive is used")
    raise AssertionError("parser.error should exit before reaching this line")


def _prompt_non_negative_int(label: str, default: int) -> int:
    while True:
        raw = input(f"{label} [{default}]: ").strip()
        if not raw:
            return default
        try:
            value = int(raw)
        except ValueError:
            print("Please enter a whole number.")
            continue
        if value < 0:
            print("Please enter a non-negative number.")
            continue
        return value


def _interactive_session(default_voice: str, default_layers: int) -> None:
    """
    Small interactive menu to demonstrate menus and while-loops.
    The Streamlit app should still live in a separate repository.
    """
    while True:
        print("echochamber menu")
        print("1. Transform text")
        print("2. Quit")
        choice = input("Choose an option [1-2]: ").strip()

        if choice == "2":
            return
        if choice != "1":
            print("Please choose 1 or 2.")
            continue

        voice_name = input(f"Voice [{default_voice}]: ").strip() or default_voice
        name = input("Persona name [User]: ").strip() or "User"
        text = input("Text to transform: ").strip()
        if not text:
            print("Text cannot be empty.")
            continue

        layers = _prompt_non_negative_int("Layers", default_layers)
        intensity = _prompt_non_negative_int("Chaos intensity", 1)
        chaos = input("Enable chaos? [y/N]: ").strip().lower() == "y"
        include_time = input("Include timestamp? [y/N]: ").strip().lower() == "y"

        persona = Persona(
            name=name,
            voice=_make_voice(voice_name),
            config=EngineConfig(include_time=include_time, chaos=chaos),
        )
        result = persona.echo_once(text, layers=layers, intensity=intensity)
        print(result["result"].transformed)
        print(f"(computed in {result['seconds']:.6f}s)")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="echochamber",
        description="Transform text through digital personas (echochamber).",
    )

    parser.add_argument(
        "text",
        nargs="?",
        help="Input text to transform (positional argument)."
    )
    parser.add_argument(
        "--input-file",
        type=Path,
        default=None,
        help="Read input text from a file path."
    )
    parser.add_argument(
        "--interactive",
        action="store_true",
        help="Launch a simple interactive menu."
    )
    parser.add_argument(
        "--voice",
        default=None,
        choices=("noir", "scifi", "therapy"),
        help="Voice: noir|scifi|therapy"
    )
    parser.add_argument("--name", default="User", help="Persona name")
    parser.add_argument(
        "--layers",
        type=_non_negative_int,
        default=None,
        help="Recursive layers"
    )
    parser.add_argument(
        "--chaos",
        action="store_true",
        help="Enable regex chaos"
    )
    parser.add_argument(
        "--time",
        action="store_true",
        help="Include timestamp"
    )
    parser.add_argument(
        "--chunk",
        type=_non_negative_int,
        default=0,
        help="Chunk size for streaming output (0 = print whole)"
    )
    parser.add_argument(
        "--intensity",
        type=_non_negative_int,
        default=1,
        help="Chaos intensity (default 1)"
    )
    parser.add_argument(
        "--conversation",
        action="store_true",
        help="Simulate a multi-persona conversation."
    )
    parser.add_argument(
        "--topic",
        default=None,
        help="Conversation topic used in simulation mode."
    )
    parser.add_argument(
        "--rounds",
        type=_non_negative_int,
        default=2,
        help="Number of conversation rounds."
    )
    parser.add_argument(
        "--participants",
        default="noir,scifi,therapy",
        help="Comma-separated voice names for simulation mode."
    )
    parser.add_argument(
        "--save-session",
        type=Path,
        default=None,
        help="Optional path to save a simulated conversation as JSON."
    )
    return parser


def main() -> None:
    # .env support (optional)
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    default_voice = os.getenv("ECHOCHAMBER_DEFAULT_VOICE", "noir")
    default_layers = _env_non_negative_int("ECHOCHAMBER_DEFAULT_LAYERS", 1)

    if args.interactive:
        _interactive_session(default_voice, default_layers)
        return

    if args.conversation:
        topic = args.topic or args.text
        if not topic:
            parser.error("--topic or text is required in conversation mode")

        conversation = Conversation(title=topic)
        for index, voice_name in enumerate(args.participants.split(","), start=1):
            normalized = voice_name.strip()
            if not normalized:
                continue
            conversation.add_personas(
                Persona(
                    name=f"{normalized.title()}-{index}",
                    voice=_make_voice(normalized),
                    tags=["cli", "conversation", normalized],
                    config=EngineConfig(
                        include_time=bool(args.time),
                        chaos=bool(args.chaos),
                    ),
                )
            )

        messages = conversation.simulate(
            topic,
            rounds=args.rounds,
            layers=args.layers if args.layers is not None else default_layers,
            intensity=args.intensity,
        )
        for message in messages:
            print(f"[{message.timestamp}] {message.speaker}: {message.content}")
        print(conversation.summary_stats())
        if args.save_session is not None:
            conversation.save(args.save_session)
            print(f"Saved session to {args.save_session}")
        return

    voice_name = args.voice or default_voice
    layers = args.layers if args.layers is not None else default_layers
    text = _resolve_input_text(parser, args.text, args.input_file)

    voice = _make_voice(voice_name)

    cfg = EngineConfig(
        include_time=bool(args.time),
        chaos=bool(args.chaos),
    )

    persona = Persona(name=args.name, voice=voice, config=cfg)
    persona.add_tags("cli")

    if args.chunk and args.chunk > 0:
        for part in persona.echo(
            text,
            chunk_size=args.chunk,
            layers=layers,
            intensity=args.intensity
        ):
            print(part, end="")
        print()
    else:
        result_dict = persona.echo_once(
            text,
            layers=layers,
            intensity=args.intensity
        )
        echo_result = result_dict["result"]
        print(echo_result.transformed)
        print(f"(computed in {result_dict['seconds']:.6f}s)")
