from __future__ import annotations

from dataclasses import dataclass, field
from typing import Iterable, Iterator, Optional

from .utils import (
    EngineConfig,
    apply_chaos,
    now_string,
    recursive_layers,
    timed,
)
from .voices import Voice


@dataclass(slots=True)
class EchoResult:
    """
    Result object for transformations.
    Demonstrates instances, docstrings, and a simple container type.
    """
    persona: str
    original: str
    transformed: str
    timestamp: Optional[str] = None


@dataclass(slots=True)
class Persona:
    """
    Persona composes a Voice (Composition).

    - name is immutable (str)
    - tags is mutable (list[str]) -> demonstrates mutable attribute
    - voice is another object (composition)
    """
    name: str
    voice: Voice
    tags: list[str] = field(default_factory=list)  # mutable instance attribute
    config: EngineConfig = field(default_factory=EngineConfig)

    # class attribute: shared default chunk size
    default_chunk_size: int = 16

    def __post_init__(self) -> None:
        # Normalize user input once so every public method sees a clean name.
        self.name = self.name.strip()
        if not self.name:
            raise ValueError("Persona name cannot be empty.")
        if self.default_chunk_size <= 0:
            raise ValueError("default_chunk_size must be positive.")

    # Magic method: "call" a Persona like a function
    def __call__(
        self, text: str, *, layers: int = 1, **kwargs: object
    ) -> EchoResult:
        return self.echo_once(text, layers=layers, **kwargs)["result"]

    # Magic method: nice debug string
    def __repr__(self) -> str:
        return (
            f"Persona(name={self.name!r}, "
            f"voice={self.voice.registry_name!r}, "
            f"tags={self.tags!r})"
        )

    # Iterable behavior: iterate over tags (Collections/Iterables)
    def __iter__(self) -> Iterator[str]:
        return iter(self.tags)

    def add_tags(self, *tags: str) -> None:
        """
        *args example: add any number of tags.
        """
        for t in tags:
            if t not in self.tags:
                self.tags.append(t)

    @timed
    def echo_once(
        self,
        text: str,
        *,
        layers: int = 1,
        config: Optional[EngineConfig] = None,
        **kwargs: object,
    ) -> dict:
        """
        **kwargs example: accepted for forward compatibility (and rubric).
        Keyword-only arguments demonstrate keyword usage.

        Returns dict so @timed can attach seconds.
        """
        if layers < 0:
            raise ValueError("layers must be non-negative.")

        cfg = config or self.config

        def one_pass(s: str) -> str:
            # The composed voice object owns style; Persona owns orchestration.
            out = self.voice.transform(s)
            if cfg.chaos:
                # allow intensity via kwargs; default argument example
                intensity = int(kwargs.get("intensity", 1))
                if intensity < 0:
                    raise ValueError("intensity must be non-negative.")
                out = apply_chaos(out, intensity=intensity)
            return out

        transformed = recursive_layers(text, one_pass, layers=layers)

        ts = now_string(cfg.time_format) if cfg.include_time else None
        if ts:
            transformed = f"[{ts}] {transformed}"

        result = EchoResult(
            persona=self.name,
            original=text,
            transformed=transformed,
            timestamp=ts,
        )

        return {"result": result}

    def echo(
        self,
        text: str,
        *,
        chunk_size: int | None = None,
        layers: int = 1,
        **kwargs: object,
    ) -> Iterable[str]:
        """
        Generator example: yields text in chunks.

        - default args: chunk_size defaults to class attribute
        - keyword-only args used
        """
        size = self.default_chunk_size if chunk_size is None else chunk_size
        if size <= 0:
            raise ValueError("chunk_size must be positive.")

        echo_result = self.echo_once(text, layers=layers, **kwargs)
        payload = echo_result["result"].transformed

        for i in range(0, len(payload), size):
            yield payload[i: i + size]
