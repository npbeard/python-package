from __future__ import annotations

from dataclasses import dataclass
from typing import ClassVar


@dataclass(slots=True)
class Voice:
    """
    Base class for voices (Inheritance target).
    Subclasses override transform().
    """
    # Class attribute (shared by all instances)
    registry_name: ClassVar[str] = "base"

    def transform(self, text: str) -> str:
        """Instance method: override in subclasses."""
        return text


@dataclass(slots=True)
class NoirVoice(Voice):
    """A detective noir style voice."""
    registry_name: ClassVar[str] = "noir"

    def transform(self, text: str) -> str:
        return f"{text} ... The city never sleeps."


@dataclass(slots=True)
class SciFiVoice(Voice):
    """A sci-fi voice."""
    registry_name: ClassVar[str] = "scifi"

    def transform(self, text: str) -> str:
        return f"{text} // signal acquired //"


@dataclass(slots=True)
class TherapyVoice(Voice):
    """A gentle therapy-style voice."""
    registry_name: ClassVar[str] = "therapy"

    def transform(self, text: str) -> str:
        return f"I hear you. Let's unpack this: {text}"