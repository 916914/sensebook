from datetime import datetime, timedelta, timezone

import pytest

from sensebook.providers.base import TutorContext
from sensebook.providers.mock import MockTutor
from sensebook.reminders import DHAKA, ReminderError, ReminderScheduler, ReminderStore


def ctx(clock):
    return TutorContext(lang="en", now_local=clock().astimezone(DHAKA).replace(tzinfo=None).isoformat(timespec="minutes"))


def test_mock_function_call_for_tomorrow_7pm(db, clock):
    reply = MockTutor().answer("remind me to revise chapter 3 tomorrow at 7 pm", ctx(clock))
    call = reply.tool_calls[0]
    assert call.name == "set_reminder"
    assert call.args["datetime_local"] == "2026-11-27T19:00" and call.args["repeat"] == "none"
    assert "chapter 3" in call.args["message"]
    store = ReminderStore(db, clock)
    r = store.from_tool_args(call.args)
    assert r.next_fire == datetime(2026, 11, 27, 13, 0, tzinfo=timezone.utc)      # 19:00 Dhaka = 13:00 UTC


def test_every_day_6am_parse(db, clock):
    call = MockTutor().answer("remind me to practise every day at 6 am", ctx(clock)).tool_calls[0]
    assert call.args["repeat"] == "daily" and call.args["datetime_local"] == "2026-11-27T06:00"


def test_validation_errors(db, clock):
    s = ReminderStore(db, clock)
    for bad in ({"message": "", "datetime_local": "2026-11-27T19:00"},
                {"message": "x", "datetime_local": "garbage"},
                {"message": "x", "datetime_local": "2026-11-27T19:00", "repeat": "hourly"},
                {"message": "x", "datetime_local": "2026-11-25T19:00"}):
        with pytest.raises(ReminderError):
            s.from_tool_args(bad)


def test_scheduler_one_off_daily_weekly_and_snooze(db, clock):
    store = ReminderStore(db, clock)
    fired = []
    sch = ReminderScheduler(store, lambda r: fired.append(r.message))
    store.from_tool_args({"message": "once", "datetime_local": "2026-11-26T17:00"})                 # +1 h
    store.from_tool_args({"message": "daily", "datetime_local": "2026-11-26T17:00", "repeat": "daily"})
    store.from_tool_args({"message": "weekly", "datetime_local": "2026-11-26T17:00", "repeat": "weekly"})
    assert sch.tick() == []
    clock.advance(minutes=59)
    assert sch.tick() == []
    clock.advance(minutes=2)
    assert sorted(fired_msgs := [r.message for r in sch.tick()]) == ["daily", "once", "weekly"]
    assert sch.tick() == []                                          # not fired twice
    daily = [r for r in store.list() if r.message == "daily"][0]
    weekly = [r for r in store.list() if r.message == "weekly"][0]
    assert daily.next_fire.astimezone(DHAKA).strftime("%d %H:%M") == "27 17:00"
    assert weekly.next_fire.astimezone(DHAKA).strftime("%d %H:%M") == "03 17:00"
    assert [r for r in store.list() if r.message == "once"][0].active is False
    clock.advance(days=1)
    assert [r.message for r in sch.tick()] == ["daily"]
    # snooze the last fire (Play/Pause): a one-off ten minutes later, the daily schedule is untouched
    assert sch.snooze_last(10).message == "daily"
    clock.advance(minutes=9)
    assert sch.tick() == []
    clock.advance(minutes=2)
    assert [r.message for r in sch.tick()] == ["daily"]


def test_reminders_survive_restart_and_missed_fire_on_boot(tmp_path, clock):
    from sensebook.db import Database
    p = str(tmp_path / "r.db")
    ReminderStore(Database(p), clock).from_tool_args({"message": "m", "datetime_local": "2026-11-26T17:00"})
    clock.advance(hours=5)
    store2 = ReminderStore(Database(p), clock)
    assert [r.message for r in store2.due()] == ["m"]
