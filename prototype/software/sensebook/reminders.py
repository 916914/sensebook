"""Reminders: structured creation (from function-call args), persistence, scheduler with injectable clock."""
from __future__ import annotations

import threading
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

from .db import Database

DHAKA = ZoneInfo("Asia/Dhaka")
REPEATS = ("none", "daily", "weekly")


class ReminderError(ValueError):
    pass


@dataclass
class Reminder:
    id: int
    message: str
    next_fire: datetime | None   # aware UTC
    repeat: str
    active: bool


def _row(r: dict) -> Reminder:
    return Reminder(r["id"], r["message"], datetime.fromisoformat(r["next_fire"]) if r["next_fire"] else None,
                    r["repeat"], bool(r["active"]))


def parse_local(dt_str: str, tz=DHAKA) -> datetime:
    """'2026-11-27T19:00' (local, naive) -> aware UTC. An explicit offset is honoured."""
    try:
        d = datetime.fromisoformat(dt_str)
    except ValueError as e:
        raise ReminderError(f"bad datetime {dt_str!r}") from e
    if d.tzinfo is None:
        d = d.replace(tzinfo=tz)
    return d.astimezone(timezone.utc)


class ReminderStore:
    def __init__(self, db: Database, clock=None, tz=DHAKA):
        self.db, self.tz = db, tz
        self.clock = clock or (lambda: datetime.now(timezone.utc))

    def from_tool_args(self, args: dict) -> Reminder:
        """Validate set_reminder function-call args and persist."""
        msg = (args.get("message") or "").strip()
        repeat = (args.get("repeat") or "none").lower()
        if not msg:
            raise ReminderError("missing message")
        if repeat not in REPEATS:
            raise ReminderError(f"bad repeat {repeat!r}")
        when = parse_local(args.get("datetime_local", ""), self.tz)
        if when <= self.clock() and repeat == "none":
            raise ReminderError("that time has already passed")
        if when <= self.clock():
            when = self._advance(when, repeat)
        return self.add(msg, when, repeat)

    def add(self, message: str, when_utc: datetime, repeat: str = "none") -> Reminder:
        rid = self.db.execute("INSERT INTO reminders(message,next_fire,repeat,active,created) VALUES(?,?,?,1,?)",
                              (message, when_utc.isoformat(), repeat, self.clock().isoformat())).lastrowid
        return self.get(rid)

    def get(self, rid: int) -> Reminder | None:
        r = self.db.one("SELECT * FROM reminders WHERE id=?", (rid,))
        return _row(r) if r else None

    def list(self, active_only=False) -> list[Reminder]:
        q = "SELECT * FROM reminders" + (" WHERE active=1" if active_only else "") + " ORDER BY next_fire"
        return [_row(r) for r in self.db.query(q)]

    def update(self, rid: int, message=None, when_utc=None, repeat=None, active=None):
        cur = self.get(rid)
        if not cur:
            raise ReminderError("no such reminder")
        self.db.execute("UPDATE reminders SET message=?, next_fire=?, repeat=?, active=? WHERE id=?",
                        (message or cur.message, (when_utc or cur.next_fire).isoformat(), repeat or cur.repeat,
                         int(cur.active if active is None else active), rid))

    def delete(self, rid: int) -> bool:
        return self.db.execute("DELETE FROM reminders WHERE id=?", (rid,)).rowcount > 0

    def _advance(self, when: datetime, repeat: str) -> datetime:
        """Next occurrence strictly after now, keeping local wall-clock time."""
        step = timedelta(days=1 if repeat == "daily" else 7)
        local = when.astimezone(self.tz)
        now = self.clock()
        while local.astimezone(timezone.utc) <= now:
            local = local + step      # naive-wall-clock add; Asia/Dhaka has no DST
        return local.astimezone(timezone.utc)

    def due(self) -> list[Reminder]:
        now = self.clock()
        return [r for r in self.list(active_only=True) if r.next_fire and r.next_fire <= now]

    def mark_fired(self, r: Reminder):
        if r.repeat == "none":
            self.db.execute("UPDATE reminders SET active=0, last_fired=? WHERE id=?", (self.clock().isoformat(), r.id))
        else:
            self.db.execute("UPDATE reminders SET next_fire=?, last_fired=? WHERE id=?",
                            (self._advance(r.next_fire, r.repeat).isoformat(), self.clock().isoformat(), r.id))

    def snooze(self, rid: int, minutes: int = 10) -> Reminder | None:
        """One-off reminders are re-armed; repeating ones get a separate one-off so the schedule is not shifted."""
        r = self.get(rid)
        if not r:
            return None
        when = self.clock() + timedelta(minutes=minutes)
        if r.repeat == "none":
            self.db.execute("UPDATE reminders SET next_fire=?, active=1 WHERE id=?", (when.isoformat(), rid))
            return self.get(rid)
        return self.add(r.message, when, "none")


class ReminderScheduler:
    """tick() is pure (testable); start() runs it on a thread. on_fire(reminder) speaks it."""

    def __init__(self, store: ReminderStore, on_fire, period: float = 5.0):
        self.store, self.on_fire, self.period = store, on_fire, period
        self.last_fired: Reminder | None = None
        self._stop = threading.Event()
        self._t: threading.Thread | None = None

    def tick(self) -> list[Reminder]:
        fired = []
        for r in self.store.due():
            self.store.mark_fired(r)      # persist first: a crash in on_fire cannot cause a fire loop
            self.last_fired = r
            fired.append(r)
            try:
                self.on_fire(r)
            except Exception:
                pass
        return fired

    def snooze_last(self, minutes: int = 10) -> Reminder | None:
        r = self.last_fired
        if r:
            self.store.snooze(r.id, minutes)
            self.last_fired = None
        return r

    def start(self):
        self._t = threading.Thread(target=self._loop, daemon=True, name="reminders")
        self._t.start()

    def _loop(self):
        while not self._stop.wait(self.period):
            self.tick()

    def stop(self):
        self._stop.set()
