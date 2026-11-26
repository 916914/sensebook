"""Deterministic offline provider: canned structured outputs, synthetic audio. No network."""
from __future__ import annotations

import hashlib
import re
from datetime import datetime, timedelta

from ..audio import tone_wav
from ..pages import PageContent, Block, UNCERTAIN_MARK
from .base import AudioClip, Speech, ToolCall, Tutor, TutorContext, TutorReply, VisionReader

CORPUS_EN = [
    ("Photosynthesis", "Plants make food using sunlight. Chlorophyll in the leaves absorbs light energy. "
                       "Carbon dioxide and water become glucose and oxygen."),
    ("Newton's Laws", "A body stays at rest unless a force acts on it. Force equals mass times acceleration. "
                      "Every action has an equal and opposite reaction."),
    ("The Water Cycle", "Water evaporates from oceans. It condenses into clouds. Rain returns it to the land."),
]


class MockVision(VisionReader):
    """Optional `registry` of (phash, printed page label) lets the synthetic camera pages carry page numbers."""
    registry: list = []
    upside_down: bool = False       # tests: pretend the book is attached upside down

    """Page text is a pure function of the image bytes, so a re-read of the same image is identical."""
    calls = 0

    def _label(self, jpeg: bytes):
        if not self.registry:
            return None
        import cv2
        import numpy as np
        from ..pages import hamming, phash
        img = cv2.imdecode(np.frombuffer(jpeg, np.uint8), cv2.IMREAD_COLOR)
        h = phash(img)
        best = min(self.registry, key=lambda r: hamming(h, r[0]))
        return best[1] if hamming(h, best[0]) <= 10 else None

    def read_page(self, jpeg: bytes, lang_hint: str = "en") -> PageContent:
        MockVision.calls += 1
        h = int(hashlib.sha1(jpeg).hexdigest(), 16)
        corpus = CORPUS_EN
        title, body = corpus[h % len(corpus)]
        label = self._label(jpeg)
        if label is not None:
            h = int(label) * 7919 + 13
            title, body = corpus[h % len(corpus)]
        blocks = [Block("heading", title), Block("paragraph", body),
                  Block("caption", f"Figure {h % 9 + 1}: illustration of {title.lower()}.")]
        if h % 5 == 0:
            blocks.append(Block("paragraph", f"The value is 3{UNCERTAIN_MARK}.", ["3?"]))
        pc = PageContent(blocks, "en", 0.92, page_label=label if label is not None else str(h % 200))
        pc.upside_down = MockVision.upside_down
        return pc


_WORD = re.compile(r"\w+", re.U)


_STOP = {"the", "and", "who", "what", "does", "this", "that", "with", "for", "are", "was", "how", "why", "from",
         "explain", "please", "tell", "about", "can", "you"}


def _toks(s):
    return {w.lower() for w in _WORD.findall(s) if len(w) > 2 and w.lower() not in _STOP}


class MockTutor(Tutor):
    """Keyword rules standing in for the LLM. Mirrors the function-calling surface."""

    def _text(self, q) -> str:
        if isinstance(q, str):
            return q
        return q.transcript or ""

    def answer(self, question, ctx: TutorContext) -> TutorReply:
        q = self._text(question).strip()
        ql = q.lower()
        if not q:
            return TutorReply("I could not hear you. Please try again.")
        if "remind" in ql:
            return TutorReply("OK, I will remind you.", [ToolCall("set_reminder", self._parse_reminder(q, ctx))])
        if m := re.search(r"remember that (.+)", ql):
            return TutorReply("Noted.", [ToolCall("remember_note", {"text": m.group(1)})])
        if "forget everything" in ql or "delete everything" in ql:
            return TutorReply("Deleting needs confirmation.", [ToolCall("forget", {"scope": "all"})])
        if m := re.search(r"forget (?:that |about )(.+)", ql):
            return TutorReply("OK.", [ToolCall("forget", {"scope": "note", "text": m.group(1)})])
        if "test me" in ql or "quiz" in ql:
            return TutorReply("Starting a quiz.", [ToolCall("start_quiz", {})])
        if "discuss" in ql or "chapter talk" in ql:
            return TutorReply("Starting a discussion.", [ToolCall("start_discussion", {})])
        if "read" in ql and "page" in ql:
            return TutorReply("Reading the page.", [ToolCall("read_page", {})])
        if "bookmark" in ql:
            return TutorReply("Bookmarked.", [ToolCall("bookmark", {"label": "bookmark"})])
        if "bangla" in ql or "bengali" in ql:
            return TutorReply("Switching to Bangla.", [ToolCall("set_language", {"language": "bn"})])
        if "english" in ql:
            return TutorReply("Switching to English.", [ToolCall("set_language", {"language": "en"})])
        # grounded answer: best-overlap sentence on the page
        from ..pages import split_sentences
        qt = _toks(q)
        sents = split_sentences(ctx.page_text)
        scored = sorted(((len(qt & _toks(s)), s) for s in sents), reverse=True)
        if scored and scored[0][0] > 0:
            return TutorReply(f"The page says: {scored[0][1]} In simple words, that is the main idea.")
        return TutorReply("That is not on this page, so I can not say from the book. I can explain it generally if you like.")

    def _parse_reminder(self, q: str, ctx: TutorContext) -> dict:
        now = datetime.fromisoformat(ctx.now_local)
        ql = q.lower()
        m = re.search(r"(\d{1,2})(?::(\d\d))?\s*(am|pm)", ql)
        hh, mm = (int(m.group(1)) % 12 + (12 if m.group(3) == "pm" else 0), int(m.group(2) or 0)) if m else (9, 0)
        repeat, base = "none", now
        if "every day" in ql or "daily" in ql:
            repeat = "daily"
        elif "every week" in ql or "weekly" in ql:
            repeat = "weekly"
        if "tomorrow" in ql:
            base = now + timedelta(days=1)
        when = base.replace(hour=hh, minute=mm, second=0, microsecond=0)
        if when <= now and "tomorrow" not in ql:
            when += timedelta(days=1)
        msg = re.sub(r"^(please )?remind me (to )?", "", ql)
        msg = re.sub(r"\b(tomorrow|every day|daily|weekly|every week)\b|\bat \d.*$", "", msg).strip(" ,.") or "reminder"
        return {"message": msg, "datetime_local": when.isoformat(timespec="minutes"), "repeat": repeat}

    def make_quiz(self, pages_text, lang, level, n_mcq=3, n_short=2):
        from ..pages import split_sentences
        sents = split_sentences(pages_text) or ["Nothing was read."]
        qs = []
        for i in range(n_mcq):
            s = sents[i % len(sents)]
            words = s.split()
            ans = words[min(2, len(words) - 1)].strip(".,")
            opts = [ans, "Mercury", "Granite", "Velocity"]
            qs.append({"type": "mcq", "question": f"Fill the blank: {s.replace(ans, '____', 1)}",
                       "options": opts, "answer": "A", "answer_text": ans, "concept": f"concept-{i % len(sents)}",
                       "explanation": s})
        for i in range(n_short):
            s = sents[(i + n_mcq) % len(sents)]
            qs.append({"type": "short", "question": f"In your own words, what does this say: {s[:40]}?",
                       "answer": s, "concept": f"concept-{(i + n_mcq) % len(sents)}", "explanation": s})
        return qs

    def grade(self, question, answer, lang):
        heard = self._text(answer).strip()
        h = heard.lower()
        if question["type"] == "mcq":
            exp = question.get("answer_text", "").lower()
            ok = bool(heard) and (h.strip(" .") in ("a", "option a", "the first one") or exp in h)
            score = 1.0 if ok else 0.0
        else:
            overlap = len(_toks(heard) & _toks(question["answer"])) / max(1, len(_toks(question["answer"])))
            score = 1.0 if overlap >= .6 else 0.5 if overlap >= .3 else 0.0
        fb = "Correct. " + question.get("explanation", "") if score >= 1 else \
            ("Partly right. " if score > 0 else "Not quite. ") + "The answer was: " + question.get("answer_text", question["answer"])
        return {"heard": heard, "score": score, "correct": score >= 0.99, "feedback": fb}

    def make_script(self, pages_text, lang, minutes):
        from ..pages import split_sentences
        sents = split_sentences(pages_text) or ["We did not read anything yet."]
        lines = [{"speaker": "learner", "text": "So, what did we just read about?"},
                 {"speaker": "teacher", "text": sents[0]}]
        for s in sents[1:6]:
            lines += [{"speaker": "learner", "text": "Can you say more about that?"}, {"speaker": "teacher", "text": s}]
        lines.append({"speaker": "learner", "text": "Got it, thanks."})
        return lines

    def host_reply(self, script_so_far, question, lang):
        q = self._text(question)
        return [{"speaker": "learner", "text": f"Good question: {q}"},
                {"speaker": "teacher", "text": "Let us think about it using what the chapter said."}]


class MockSpeech(Speech):
    """Beeps: pitch encodes the voice, length encodes text length (capped, so tests are fast)."""
    sample_rate = 16000
    PITCH = {"reader": 440, "explainer": 330, "learner": 523, "teacher": 392}

    def __init__(self):
        self.log: list[tuple[str, str]] = []

    def synthesize(self, text, role, lang, speed=1.0):
        self.log.append((role, text))
        return tone_wav(self.PITCH.get(role, 440), min(0.05 + len(text) * 0.002, 0.4) / max(speed, .5), self.sample_rate)

    def synthesize_dialogue(self, lines, lang):
        import numpy as np
        from ..audio import wav_to_pcm, pcm_to_wav
        pcm = []
        for ln in lines:
            self.log.append((ln["speaker"], ln["text"]))
            p, _ = wav_to_pcm(tone_wav(self.PITCH.get(ln["speaker"], 440), min(0.05 + len(ln["text"]) * 0.002, 0.3), self.sample_rate))
            pcm.append(p)
        return pcm_to_wav(np.concatenate(pcm) if pcm else np.zeros(0, np.int16), self.sample_rate)
