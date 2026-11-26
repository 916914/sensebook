"""Opt-in learner memory. Everything personal is refused until memory is enabled.

Functional data that is not a personal profile (reminders, the page cache) works regardless.
"""
from __future__ import annotations

import hashlib
import hmac
import json
import os
from datetime import datetime, timezone

from .db import Database

PERSONAL_TABLES = ["notes", "concepts", "sessions", "bookmarks", "quiz_results"]
PROFILE_DEFAULTS = {"language": "bn", "level": "class 9", "voice_speed": "1.0", "memory_enabled": "0",
                    "headphone_pref": "speaker", "light_level": "0.4", "current_book": "My book", "accessibility_mode": "0"}


def now_iso() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Memory:
    def __init__(self, db: Database, clock=None):
        self.db = db
        self._clock = clock or now_iso

    # ---- profile / settings ----
    def get(self, key: str, default: str | None = None) -> str | None:
        r = self.db.one("SELECT value FROM profile WHERE key=?", (key,))
        if r:
            return r["value"]
        return PROFILE_DEFAULTS.get(key, default)

    def set(self, key: str, value) -> None:
        self.db.execute("INSERT INTO profile(key,value) VALUES(?,?) ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                        (key, str(value)))

    @property
    def enabled(self) -> bool:
        return self.get("memory_enabled") == "1"

    def set_enabled(self, on: bool) -> None:
        self.set("memory_enabled", "1" if on else "0")

    # ---- guardian PIN (PBKDF2; the PIN never leaves the device) ----
    def pin_is_set(self) -> bool:
        return self.db.one("SELECT 1 AS x FROM profile WHERE key='pin_hash'") is not None

    def set_pin(self, pin: str) -> None:
        if not (pin.isdigit() and 4 <= len(pin) <= 8):
            raise ValueError("PIN must be 4 to 8 digits")
        salt = os.urandom(16)
        h = hashlib.pbkdf2_hmac("sha256", pin.encode(), salt, 120_000)
        self.set("pin_hash", salt.hex() + ":" + h.hex())

    def check_pin(self, pin: str) -> bool:
        v = self.db.one("SELECT value FROM profile WHERE key='pin_hash'")
        if not v:
            return False
        salt, h = v["value"].split(":")
        cand = hashlib.pbkdf2_hmac("sha256", pin.encode(), bytes.fromhex(salt), 120_000)
        return hmac.compare_digest(cand.hex(), h)

    # ---- notes ----
    def add_note(self, text: str) -> int | None:
        if not self.enabled:
            return None
        return self.db.execute("INSERT INTO notes(text,created) VALUES(?,?)", (text.strip(), self._clock())).lastrowid

    def list_notes(self) -> list[dict]:
        return self.db.query("SELECT * FROM notes ORDER BY id")

    def delete_note(self, note_id: int) -> bool:
        return self.db.execute("DELETE FROM notes WHERE id=?", (note_id,)).rowcount > 0

    def relevant_notes(self, text: str, limit: int = 5) -> list[str]:
        """Cheap keyword-overlap retrieval (no embeddings on a Zero 2 W)."""
        if not self.enabled:
            return []
        words = {w for w in text.lower().split() if len(w) > 2}
        scored = []
        for n in self.list_notes():
            s = len(words & set(n["text"].lower().split()))
            scored.append((s, n["id"], n["text"]))
        scored.sort(key=lambda t: (-t[0], -t[1]))
        return [t[2] for t in scored[:limit] if t[0] > 0] or [t[2] for t in scored[:2]]

    # ---- bookmarks / sessions / quiz results ----
    def add_bookmark(self, book: str, page_id: int | None, label: str) -> int | None:
        if not self.enabled:
            return None
        return self.db.execute("INSERT INTO bookmarks(book,page_id,label,created) VALUES(?,?,?,?)",
                               (book, page_id, label, self._clock())).lastrowid

    def list_bookmarks(self) -> list[dict]:
        return self.db.query("SELECT * FROM bookmarks ORDER BY id")

    def start_session(self) -> int | None:
        if not self.enabled:
            return None
        return self.db.execute("INSERT INTO sessions(started) VALUES(?)", (self._clock(),)).lastrowid

    def update_session(self, sid: int | None, pages_read: int, seconds: int) -> None:
        if sid and self.enabled:
            self.db.execute("UPDATE sessions SET pages_read=?, seconds=?, ended=? WHERE id=?",
                            (pages_read, seconds, self._clock(), sid))

    def add_quiz_result(self, **r) -> None:
        if not self.enabled:
            return
        self.db.execute(
            "INSERT INTO quiz_results(ts,quiz_id,question,qtype,concept,expected,answer_heard,score,feedback)"
            " VALUES(?,?,?,?,?,?,?,?,?)",
            (self._clock(), r.get("quiz_id"), r.get("question"), r.get("qtype"), r.get("concept"),
             r.get("expected"), r.get("answer_heard"), r.get("score"), r.get("feedback")))

    def quiz_history(self) -> list[dict]:
        return self.db.query("SELECT * FROM quiz_results ORDER BY id DESC")

    # ---- summary for the tutor prompt ----
    def context_for_tutor(self, question: str) -> dict:
        return {"level": self.get("level"), "notes": self.relevant_notes(question),
                "weak_concepts": [c["name"] for c in self.db.query(
                    "SELECT name FROM concepts ORDER BY mastery ASC LIMIT 3")] if self.enabled else []}

    # ---- stats for dashboard ----
    def stats(self, today_prefix: str) -> dict:
        s = self.db.one("SELECT COALESCE(SUM(seconds),0) AS sec, COALESCE(SUM(pages_read),0) AS pages "
                        "FROM sessions WHERE started LIKE ?", (today_prefix + "%",))
        q = self.db.one("SELECT AVG(score) AS avg, COUNT(*) AS n FROM quiz_results")
        return {"study_minutes_today": round(s["sec"] / 60, 1), "pages_today": s["pages"],
                "quiz_avg": None if q["avg"] is None else round(q["avg"] * 100), "quiz_count": q["n"]}

    # ---- export / delete ----
    def export_all(self) -> dict:
        out = {"exported": self._clock(), "profile": {k: v for k, v in
               ((r["key"], r["value"]) for r in self.db.query("SELECT * FROM profile")) if k != "pin_hash"}}
        for t in PERSONAL_TABLES + ["reminders"]:
            out[t] = self.db.query(f"SELECT * FROM {t}")
        return out

    def export_json(self) -> str:
        return json.dumps(self.export_all(), ensure_ascii=False, indent=2)

    def spoken_summary(self) -> str:
        return (f"I remember {len(self.list_notes())} notes, "
                f"{self.db.one('SELECT COUNT(*) c FROM concepts')['c']} concepts and "
                f"{len(self.list_bookmarks())} bookmarks.")

    def delete_everything(self, include_pages: bool = True, include_reminders: bool = True) -> None:
        """Wipe all personal data. The PIN and memory switch survive unless the caller resets them."""
        for t in PERSONAL_TABLES:
            self.db.execute(f"DELETE FROM {t}")
        if include_reminders:
            self.db.execute("DELETE FROM reminders")
        if include_pages:
            self.db.execute("DELETE FROM pages")
        self.db.execute("DELETE FROM profile WHERE key IN ('level','current_book')")

    def delete_note_matching(self, text: str) -> int:
        t = f"%{text.lower()}%"
        return self.db.execute("DELETE FROM notes WHERE lower(text) LIKE ?", (t,)).rowcount
