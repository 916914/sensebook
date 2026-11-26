from __future__ import annotations

from .base import (AudioClip, ProviderError, ProviderUnavailable, Speech, ToolCall, Tutor, TutorContext,
                   TutorReply, VisionReader)


def make_providers(name: str, cfg: dict):
    """Return (VisionReader, Tutor, Speech). Add a vendor by adding a branch here."""
    if name == "mock":
        from .mock import MockSpeech, MockTutor, MockVision
        return MockVision(), MockTutor(), MockSpeech()
    if name == "gemini":
        from .gemini import GeminiSpeech, GeminiTutor, GeminiVision
        from .gemini import _client
        client = _client(None)
        return GeminiVision(cfg, client=client), GeminiTutor(cfg, client=client), GeminiSpeech(cfg, client=client)
    raise ValueError(f"unknown provider {name!r}")
