"""Tool schema for function calling and the TutorService that ties provider + memory + app actions."""
from __future__ import annotations

from typing import Callable

from .providers.base import AudioClip, ToolCall, Tutor, TutorContext, TutorReply

TOOLS = [
    {"name": "set_reminder",
     "description": "Create a reminder. Resolve relative times (tomorrow, in 2 hours) against the current local time.",
     "parameters": {"type": "object", "properties": {
         "message": {"type": "string", "description": "What to remind, short, in the user's language"},
         "datetime_local": {"type": "string", "description": "First fire time, ISO 8601 local time without offset, e.g. 2026-11-27T19:00"},
         "repeat": {"type": "string", "enum": ["none", "daily", "weekly"]}},
         "required": ["message", "datetime_local"]}},
    {"name": "remember_note", "description": "Save something the user asked to be remembered.",
     "parameters": {"type": "object", "properties": {"text": {"type": "string"}}, "required": ["text"]}},
    {"name": "start_quiz", "description": "Start a spoken quiz on the pages read this session.",
     "parameters": {"type": "object", "properties": {"num_questions": {"type": "integer"}}}},
    {"name": "start_discussion", "description": "Start a two-host audio discussion of the pages read this session.",
     "parameters": {"type": "object", "properties": {"minutes": {"type": "integer"}}}},
    {"name": "read_page", "description": "Read the current page aloud verbatim.",
     "parameters": {"type": "object", "properties": {}}},
    {"name": "bookmark", "description": "Bookmark the current page.",
     "parameters": {"type": "object", "properties": {"label": {"type": "string"}}}},
    {"name": "set_language", "description": "Change the spoken language.",
     "parameters": {"type": "object", "properties": {"language": {"type": "string", "enum": ["bn", "en"]}}, "required": ["language"]}},
    {"name": "forget", "description": "Delete memory. scope=note deletes notes matching text; scope=all deletes everything (needs physical confirmation).",
     "parameters": {"type": "object", "properties": {"scope": {"type": "string", "enum": ["note", "all"]}, "text": {"type": "string"}}, "required": ["scope"]}},
]


class TutorService:
    """handlers: tool name -> fn(args) -> optional spoken confirmation (str)."""

    def __init__(self, tutor: Tutor, memory, tz, clock, handlers: dict[str, Callable[[dict], str | None]]):
        self.tutor, self.memory, self.tz, self.clock, self.handlers = tutor, memory, tz, clock, handlers
        self.history: list[tuple[str, str]] = []

    def context(self, lang: str, page_text: str, recent: list[str], question_hint: str = "") -> TutorContext:
        now = self.clock().astimezone(self.tz).replace(tzinfo=None)
        return TutorContext(lang=lang, now_local=now.isoformat(timespec="minutes"), timezone=str(self.tz),
                            page_text=page_text, recent_pages=recent,
                            memory={**self.memory.context_for_tutor(question_hint)}, history=list(self.history))

    def ask(self, clip: "AudioClip | str", lang: str, page_text: str, recent: list[str]) -> tuple[str, list[str]]:
        """Returns (explanation_text, confirmations). Tool calls are executed; unknown tools are ignored."""
        reply: TutorReply = self.tutor.answer(clip, self.context(lang, page_text, recent))
        confirmations = []
        for call in reply.tool_calls:
            fn = self.handlers.get(call.name)
            if fn:
                msg = fn(call.args)
                if msg:
                    confirmations.append(msg)
        if reply.text:
            self.history.append(("tutor", reply.text))
            self.history = self.history[-12:]
        return reply.text, confirmations
