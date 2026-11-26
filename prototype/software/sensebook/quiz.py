"""Spaced repetition (SM-2) and the spoken quiz flow."""
from __future__ import annotations

import uuid
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone

from .db import Database
from .providers.base import AudioClip, Tutor


def sm2(ease: float, reps: int, interval: float, quality: int) -> tuple[float, int, float]:
    """Classic SM-2. quality 0..5. Returns (ease, repetitions, interval_days)."""
    quality = max(0, min(5, quality))
    if quality < 3:
        reps, interval = 0, 1.0
    else:
        reps += 1
        interval = 1.0 if reps == 1 else 6.0 if reps == 2 else round(interval * ease, 1)
    ease = max(1.3, ease + 0.1 - (5 - quality) * (0.08 + (5 - quality) * 0.02))
    return ease, reps, interval


class ConceptTracker:
    def __init__(self, db: Database, memory, clock=None):
        self.db, self.memory = db, memory
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def record(self, concept: str, score: float, source_page: str | None = None):
        if not self.memory.enabled or not concept:
            return
        row = self.db.one("SELECT * FROM concepts WHERE name=?", (concept,)) or {
            "mastery": 0.0, "ease": 2.5, "repetitions": 0, "interval_days": 0.0}
        ease, reps, interval = sm2(row["ease"], row["repetitions"], row["interval_days"], round(score * 5))
        mastery = round(0.6 * row["mastery"] + 0.4 * score, 3) if row["repetitions"] or row["mastery"] else round(score, 3)
        now = self.clock()
        due = (now + timedelta(days=interval)).isoformat()
        self.db.execute(
            "INSERT INTO concepts(name,mastery,ease,interval_days,repetitions,due,last_review,source_page) VALUES(?,?,?,?,?,?,?,?)"
            " ON CONFLICT(name) DO UPDATE SET mastery=?,ease=?,interval_days=?,repetitions=?,due=?,last_review=?",
            (concept, mastery, ease, interval, reps, due, now.isoformat(), source_page,
             mastery, ease, interval, reps, due, now.isoformat()))

    def due(self) -> list[dict]:
        return self.db.query("SELECT * FROM concepts WHERE due <= ? ORDER BY due", (self.clock().isoformat(),))

    def all(self) -> list[dict]:
        return self.db.query("SELECT * FROM concepts ORDER BY mastery")


@dataclass
class QuizOutcome:
    quiz_id: str
    results: list[dict]

    @property
    def score(self) -> float:
        return sum(r["score"] for r in self.results) / max(1, len(self.results))


class QuizSession:
    """io.speak(text, role) and io.listen() -> AudioClip|None (None = nothing heard). Sequential and testable."""

    def __init__(self, tutor: Tutor, memory, tracker: ConceptTracker, io, lang: str, level: str = "class 9"):
        self.tutor, self.memory, self.tracker, self.io, self.lang, self.level = tutor, memory, tracker, io, lang, level

    def run(self, pages_text: str, n_mcq=3, n_short=2, source_page: str | None = None) -> QuizOutcome:
        qid = uuid.uuid4().hex[:8]
        questions = self.tutor.make_quiz(pages_text, self.lang, self.level, n_mcq, n_short)
        results = []
        for i, q in enumerate(questions, 1):
            text = f"Question {i}. {q['question']}"
            if q["type"] == "mcq":
                text += " " + " ".join(f"{'ABCD'[j]}: {o}." for j, o in enumerate(q["options"]))
            self.io.speak(text, "explainer")
            clip = self.io.listen()
            if clip is None:
                self.io.speak("I did not hear an answer. Skipping.", "explainer")
                g = {"heard": "", "score": 0.0, "correct": False, "feedback": f"The answer was {q.get('answer_text', q['answer'])}."}
            else:
                g = self.tutor.grade(q, clip, self.lang)
            self.io.speak(g["feedback"], "explainer")
            r = {"quiz_id": qid, "question": q["question"], "qtype": q["type"], "concept": q.get("concept"),
                 "expected": q.get("answer_text", q["answer"]), "answer_heard": g["heard"],
                 "score": float(g["score"]), "feedback": g["feedback"]}
            self.memory.add_quiz_result(**r)
            self.tracker.record(q.get("concept"), r["score"], source_page)
            results.append(r)
        out = QuizOutcome(qid, results)
        self.io.speak(f"You scored {round(out.score * 100)} percent.", "explainer")
        return out
