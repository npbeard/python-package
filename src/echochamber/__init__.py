"""
echochamber: A narrative sentiment & chaos engine.

Public API exports are defined here so users can do:

from echochamber import Persona, NoirVoice
"""
__version__ = "0.1.0"

from .personas import Persona, EchoResult
from .voices import Voice, NoirVoice, SciFiVoice, TherapyVoice
from .utils import EngineConfig, timed

__all__ = [
    "__version__",
    "Persona",
    "EchoResult",
    "Voice",
    "NoirVoice",
    "SciFiVoice",
    "TherapyVoice",
    "EngineConfig",
    "timed",
]
