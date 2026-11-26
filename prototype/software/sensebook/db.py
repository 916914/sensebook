"""One SQLite file for everything (WAL, thread-safe via a lock)."""
from __future__ import annotations

import sqlite3
import threading

SCHEMA = """
CREATE TABLE IF NOT EXISTS profile (key TEXT PRIMARY KEY, value TEXT);
CREATE TABLE IF NOT EXISTS notes (id INTEGER PRIMARY KEY, text TEXT NOT NULL, created TEXT NOT NULL);
CREATE TABLE IF NOT EXISTS concepts (
  name TEXT PRIMARY KEY, mastery REAL DEFAULT 0, ease REAL DEFAULT 2.5, interval_days REAL DEFAULT 0,
  repetitions INTEGER DEFAULT 0, due TEXT, last_review TEXT, source_page TEXT);
CREATE TABLE IF NOT EXISTS sessions (
  id INTEGER PRIMARY KEY, started TEXT NOT NULL, ended TEXT, pages_read INTEGER DEFAULT 0, seconds INTEGER DEFAULT 0);
CREATE TABLE IF NOT EXISTS bookmarks (id INTEGER PRIMARY KEY, book TEXT, page_id INTEGER, label TEXT, created TEXT);
CREATE TABLE IF NOT EXISTS quiz_results (
  id INTEGER PRIMARY KEY, ts TEXT NOT NULL, quiz_id TEXT, question TEXT, qtype TEXT, concept TEXT,
  expected TEXT, answer_heard TEXT, score REAL, feedback TEXT);
CREATE TABLE IF NOT EXISTS reminders (
  id INTEGER PRIMARY KEY, message TEXT NOT NULL, next_fire TEXT, repeat TEXT DEFAULT 'none',
  active INTEGER DEFAULT 1, created TEXT, last_fired TEXT);
CREATE TABLE IF NOT EXISTS pages (
  id INTEGER PRIMARY KEY, phash TEXT NOT NULL, book TEXT, page_label TEXT, lang TEXT, confidence REAL,
  blocks_json TEXT NOT NULL, first_seen TEXT, last_seen TEXT, seen_count INTEGER DEFAULT 1);
CREATE INDEX IF NOT EXISTS pages_hash ON pages(phash);
"""


class Database:
    def __init__(self, path: str = ":memory:"):
        self.path = path
        self._lock = threading.RLock()
        self.conn = sqlite3.connect(path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        if path != ":memory:":
            self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.executescript(SCHEMA)
        self.conn.commit()

    def execute(self, sql: str, args: tuple = ()) -> sqlite3.Cursor:
        with self._lock:
            cur = self.conn.execute(sql, args)
            self.conn.commit()
            return cur

    def query(self, sql: str, args: tuple = ()) -> list[dict]:
        with self._lock:
            return [dict(r) for r in self.conn.execute(sql, args).fetchall()]

    def one(self, sql: str, args: tuple = ()) -> dict | None:
        rows = self.query(sql, args)
        return rows[0] if rows else None

    def close(self):
        with self._lock:
            self.conn.close()
