"""
Tests for echochamber.voices
-----------------------------
Covers:
- Inheritance: each concrete voice is a subclass of Voice
- Class attributes: registry_name is set correctly per subclass
- Instance methods: transform() produces the expected suffix/prefix
- Polymorphism: a list of different Voice instances can be called uniformly
"""

from __future__ import annotations

import pytest

from echochamber.voices import NoirVoice, SciFiVoice, TherapyVoice, Voice


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

ALL_VOICE_CLASSES = [NoirVoice, SciFiVoice, TherapyVoice]


# ---------------------------------------------------------------------------
# Base class
# ---------------------------------------------------------------------------

class TestBaseVoice:
    """Voice base class behaves as a pass-through transformer."""

    def test_base_transform_returns_input_unchanged(self):
        voice = Voice()
        assert voice.transform("hello") == "hello"

    def test_base_registry_name(self):
        assert Voice.registry_name == "base"


# ---------------------------------------------------------------------------
# Inheritance checks
# ---------------------------------------------------------------------------

class TestInheritance:
    """All concrete voices are proper subclasses of Voice."""

    @pytest.mark.parametrize("voice_cls", ALL_VOICE_CLASSES)
    def test_is_subclass_of_voice(self, voice_cls):
        assert issubclass(voice_cls, Voice), (
            f"{voice_cls.__name__} must inherit from Voice"
        )

    @pytest.mark.parametrize("voice_cls", ALL_VOICE_CLASSES)
    def test_instance_is_voice(self, voice_cls):
        instance = voice_cls()
        assert isinstance(instance, Voice)


# ---------------------------------------------------------------------------
# Class attributes: registry_name
# ---------------------------------------------------------------------------

class TestRegistryNames:
    """Each voice subclass declares a unique registry_name class attribute."""

    def test_noir_registry_name(self):
        assert NoirVoice.registry_name == "noir"

    def test_scifi_registry_name(self):
        assert SciFiVoice.registry_name == "scifi"

    def test_therapy_registry_name(self):
        assert TherapyVoice.registry_name == "therapy"

    def test_registry_names_are_unique(self):
        names = [cls.registry_name for cls in ALL_VOICE_CLASSES]
        assert len(names) == len(set(names)), "Every voice must have a unique registry_name"

    def test_instance_registry_name_matches_class(self):
        """Instance attribute must equal the class attribute (slots-safe check)."""
        for cls in ALL_VOICE_CLASSES:
            instance = cls()
            assert instance.registry_name == cls.registry_name


# ---------------------------------------------------------------------------
# NoirVoice
# ---------------------------------------------------------------------------

class TestNoirVoice:
    """Noir voice appends a hard-boiled city tagline."""

    def test_transform_contains_original_text(self):
        voice = NoirVoice()
        result = voice.transform("It was a dark night")
        assert "It was a dark night" in result

    def test_transform_appends_city_tagline(self):
        voice = NoirVoice()
        result = voice.transform("She walked in")
        assert "city never sleeps" in result

    def test_transform_empty_string(self):
        """Edge-case: transforming an empty string should not raise."""
        voice = NoirVoice()
        result = voice.transform("")
        assert isinstance(result, str)
        assert len(result) > 0  # tagline is still appended


# ---------------------------------------------------------------------------
# SciFiVoice
# ---------------------------------------------------------------------------

class TestSciFiVoice:
    """Sci-fi voice appends a signal-acquisition marker."""

    def test_transform_contains_original_text(self):
        voice = SciFiVoice()
        result = voice.transform("Launching in T-minus 10")
        assert "Launching in T-minus 10" in result

    def test_transform_appends_signal_marker(self):
        voice = SciFiVoice()
        result = voice.transform("Engage warp drive")
        assert "signal acquired" in result

    def test_transform_empty_string(self):
        voice = SciFiVoice()
        result = voice.transform("")
        assert "signal acquired" in result


# ---------------------------------------------------------------------------
# TherapyVoice
# ---------------------------------------------------------------------------

class TestTherapyVoice:
    """Therapy voice prepends an empathetic preamble."""

    def test_transform_contains_original_text(self):
        voice = TherapyVoice()
        result = voice.transform("I feel overwhelmed")
        assert "I feel overwhelmed" in result

    def test_transform_prepends_preamble(self):
        voice = TherapyVoice()
        result = voice.transform("Something is wrong")
        assert result.startswith("I hear you"), (
            "TherapyVoice must prepend 'I hear you'"
        )

    def test_transform_empty_string(self):
        voice = TherapyVoice()
        result = voice.transform("")
        assert "I hear you" in result


# ---------------------------------------------------------------------------
# Polymorphism: uniform interface across voice types
# ---------------------------------------------------------------------------

class TestPolymorphism:
    """
    A list of different Voice objects can all be called through the same
    interface — this is a practical demonstration of inheritance /
    polymorphism in the course rubric.
    """

    def test_all_voices_transform_returns_string(self):
        voices: list[Voice] = [NoirVoice(), SciFiVoice(), TherapyVoice()]
        for voice in voices:
            result = voice.transform("test input")
            assert isinstance(result, str), (
                f"{type(voice).__name__}.transform() must return a str"
            )

    def test_all_voices_output_contains_input(self):
        """Every voice must preserve the original text somewhere in the output."""
        payload = "unique test payload"
        voices: list[Voice] = [NoirVoice(), SciFiVoice(), TherapyVoice()]
        for voice in voices:
            assert payload in voice.transform(payload), (
                f"{type(voice).__name__}.transform() dropped the original text"
            )

    def test_voices_produce_distinct_outputs(self):
        """Different voices must produce different stylistic results."""
        text = "Hello world"
        outputs = {type(v).__name__: v.transform(text) for v in [NoirVoice(), SciFiVoice(), TherapyVoice()]}
        unique_outputs = set(outputs.values())
        assert len(unique_outputs) == 3, (
            "Each voice should produce a stylistically distinct transformation"
        )
