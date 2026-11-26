"""Vendor-neutral provider interfaces. Add a vendor by implementing these three ABCs."""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass, field

from ..pages import PageContent


class ProviderError(Exception):
    """Cloud call failed in a way retrying will not fix."""


class ProviderUnavailable(ProviderError):
    """No internet / service unreachable: the app falls back to cache and offline TTS."""


@dataclass
class AudioClip:
    wav: bytes
    transcript: str | None = None   # only set by tests / mock mic; real providers hear the audio itself


@dataclass
class ToolCall:
    name: str
    args: dict


@dataclass
class TutorContext:
    lang: str                       # bn | en
    now_local: str                  # ISO local time, for resolving "tomorrow at 7 pm"
    timezone: str = "Asia/Dhaka"
    page_text: str = ""
    recent_pages: list[str] = field(default_factory=list)
    memory: dict = field(default_factory=dict)
    history: list[tuple[str, str]] = field(default_factory=list)   # (role, text)


@dataclass
class TutorReply:
    text: str
    tool_calls: list[ToolCall] = field(default_factory=list)


class VisionReader(ABC):
    @abstractmethod
    def read_page(self, jpeg: bytes, lang_hint: str = "bn") -> PageContent:
        """Transcribe one page image faithfully, in reading order, as typed blocks."""


class Tutor(ABC):
    @abstractmethod
    def answer(self, question: "AudioClip | str", ctx: TutorContext) -> TutorReply: ...

    @abstractmethod
    def make_quiz(self, pages_text: str, lang: str, level: str, n_mcq: int = 3, n_short: int = 2) -> list[dict]:
        """[{type: mcq|short, question, options?, answer, concept, explanation}]"""

    @abstractmethod
    def grade(self, question: dict, answer: "AudioClip | str", lang: str) -> dict:
        """{heard, score 0..1, correct, feedback}"""

    @abstractmethod
    def make_script(self, pages_text: str, lang: str, minutes: int) -> list[dict]:
        """[{speaker: learner|teacher, text}]"""

    @abstractmethod
    def host_reply(self, script_so_far: list[dict], question: "AudioClip | str", lang: str) -> list[dict]: ...


class Speech(ABC):
    sample_rate: int = 24000

    @abstractmethod
    def synthesize(self, text: str, role: str, lang: str, speed: float = 1.0) -> bytes:
        """role: reader | explainer | chime-less. Returns WAV bytes."""

    @abstractmethod
    def synthesize_dialogue(self, lines: list[dict], lang: str) -> bytes:
        """lines: [{speaker: learner|teacher, text}] -> one WAV with two voices."""
