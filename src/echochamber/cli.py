from __future__ import annotations

import argparse
import os
from dotenv import load_dotenv

from .personas import Persona
from .voices import Voice, NoirVoice, SciFiVoice, TherapyVoice
from .utils import EngineConfig


def _make_voice(name: str) -> Voice:
    name = name.lower().strip()
    if name == "noir":
        return NoirVoice()
    if name in ("scifi", "sci-fi", "sci_fi"):
        return SciFiVoice()
    if name in ("therapy", "therapist"):
        return TherapyVoice()
    raise SystemExit(f"Unknown voice: {name}. Use noir|scifi|therapy.")


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="echochamber",
        description="Transform text through digital personas (echochamber).",
    )

    parser.add_argument(
        "text",
        help="Input text to transform (positional argument)."
    )
    parser.add_argument(
        "--voice",
        default=None,
        help="Voice: noir|scifi|therapy"
    )
    parser.add_argument("--name", default="User", help="Persona name")
    parser.add_argument(
        "--layers",
        type=int,
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
        type=int,
        default=0,
        help="Chunk size for streaming output (0 = print whole)"
    )
    parser.add_argument(
        "--intensity",
        type=int,
        default=1,
        help="Chaos intensity (default 1)"
    )
    return parser


def main() -> None:
    # .env support (optional)
    load_dotenv()

    parser = build_parser()
    args = parser.parse_args()

    default_voice = os.getenv("ECHOCHAMBER_DEFAULT_VOICE", "noir")
    default_layers = int(os.getenv("ECHOCHAMBER_DEFAULT_LAYERS", "1"))

    voice_name = args.voice or default_voice
    layers = args.layers if args.layers is not None else default_layers

    voice = _make_voice(voice_name)

    cfg = EngineConfig(
        include_time=bool(args.time),
        chaos=bool(args.chaos),
    )

    persona = Persona(name=args.name, voice=voice, config=cfg)
    persona.add_tags("cli")

    if args.chunk and args.chunk > 0:
        for part in persona.echo(
            args.text,
            chunk_size=args.chunk,
            layers=layers,
            intensity=args.intensity
        ):
            print(part, end="")
        print()
    else:
        result_dict = persona.echo_once(
            args.text,
            layers=layers,
            intensity=args.intensity
        )
        echo_result = result_dict["result"]
        print(echo_result.transformed)
        print(f"(computed in {result_dict['seconds']:.6f}s)")