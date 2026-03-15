from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime
from functools import wraps
import copy
import re
import time
from typing import Any, Callable


# -----------------------------
# Hashable immutable config
# -----------------------------
@dataclass(frozen=True, slots=True)
class EngineConfig:
    """
    Immutable, hashable configuration object (frozen dataclass).
    Can be used as a dict key or stored in a set.
    """
    include_time: bool = True
    time_format: str = "%Y-%m-%d %H:%M"
    chaos: bool = False


# -----------------------------
# Decorator example
# -----------------------------
def timed(fn: Callable[..., Any]) -> Callable[..., Any]:
    """
    Decorator that measures runtime (seconds)
    and attaches it to the return value
    if the return is a dict-like object, otherwise returns (result, seconds).
    """
    @wraps(fn)
    def wrapper(*args: Any, **kwargs: Any) -> Any:
        start = time.perf_counter()
        result = fn(*args, **kwargs)
        elapsed = time.perf_counter() - start

        if isinstance(result, dict):
            result["seconds"] = elapsed
            return result
        return result, elapsed

    return wrapper


# -----------------------------
# Datetime formatting
# -----------------------------
def now_string(fmt: str = "%Y-%m-%d %H:%M") -> str:
    """
    Return current local time formatted as a string.
    Default format: YYYY-MM-DD HH:MM
    """
    return datetime.now().strftime(fmt)


# -----------------------------
# Regex "chaos" effects
# -----------------------------
_PUNCT_RE = re.compile(r"([!?.,])\1+")
_VOWEL_RE = re.compile(r"[aeiouAEIOU]")


def apply_chaos(text: str, intensity: int = 1) -> str:
    """
    Apply a mild chaotic transformation using regex.
    - Compress repeated punctuation: "!!!" -> "!"
    - Replace some vowels with '*'
    intensity: higher => more vowel masking
    """
    if intensity < 1:
        return text

    text = _PUNCT_RE.sub(r"\1", text)

    # mask every Nth vowel where N depends on intensity
    step = max(1, 4 - min(intensity, 3))  # intensity 1->3 maps to step 3..1
    vowels = list(_VOWEL_RE.finditer(text))
    chars = list(text)
    for i, m in enumerate(vowels):
        if i % step == 0:
            chars[m.start()] = "*"
    return "".join(chars)


# -----------------------------
# Recursion
# -----------------------------
def recursive_layers(text: str, fn: Callable[[str], str], layers: int) -> str:
    """
    Apply fn to text recursively 'layers' times.
    Demonstrates recursion; ensure layers is small to avoid deep recursion.
    """
    return text if layers <= 0 else recursive_layers(fn(text), fn, layers - 1)


# -----------------------------
# Shallow vs deep copy helpers
# -----------------------------
def shallow_copy(obj: Any) -> Any:
    """Return a shallow copy of obj."""
    return copy.copy(obj)


def deep_copy(obj: Any) -> Any:
    """Return a deep copy of obj."""
    return copy.deepcopy(obj)
