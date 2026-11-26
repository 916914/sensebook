import json

import pytest

from sensebook.webapp import create_app


@pytest.fixture
def client(make_app):
    core = make_app()
    web = create_app(core, secret="test")
    return web.test_client(), core


def token(c):
    with c.session_transaction() as s:
        return s["csrf"]


def test_pin_gate_setup_login_and_flow(client):
    c, core = client
    assert c.get("/").status_code == 302 and "/setup" in c.get("/").headers["Location"]
    assert c.post("/setup", data={"pin": "12"}).status_code == 200            # too short
    assert c.post("/setup", data={"pin": "4321"}).status_code == 302
    assert c.get("/").status_code == 200
    c.post("/logout", data={"csrf": token(c)})
    assert c.get("/memory").status_code == 302
    assert c.post("/login", data={"pin": "0000"}).status_code == 200
    assert c.post("/login", data={"pin": "4321"}).status_code == 302
    for page in ("/", "/memory", "/reminders", "/quizzes", "/library", "/settings"):
        r = c.get(page)
        assert r.status_code == 200 and b"<main" in r.data and b'lang="en"' in r.data


def test_csrf_enforced_settings_memory_reminders_export_delete(client):
    c, core = client
    c.post("/setup", data={"pin": "4321"})
    c.get("/")
    assert c.post("/settings", data={"language": "en"}).status_code == 400   # no csrf
    t = token(c)
    c.post("/settings", data={"csrf": t, "language": "en", "voice_speed": "0.9", "memory_enabled": "on",
                              "headphone_pref": "headphones", "light_level": "0.6"})
    assert core.memory.enabled and core.memory.get("language") == "en" and core.memory.get("headphone_pref") == "headphones"
    assert core.router.speaker_muted() and not core.hw.amp_on                # private mode: amp SD low
    core.memory.add_note("hello note")
    r = c.get("/export.json")
    assert json.loads(r.data)["notes"][0]["text"] == "hello note"
    c.post("/reminders", data={"csrf": t, "action": "create", "message": "study", "when": "2030-01-01T07:00", "repeat": "daily"})
    assert [r.message for r in core.reminders.list()] == ["study"]
    rid = core.reminders.list()[0].id
    c.post("/reminders", data={"csrf": t, "action": "edit", "id": rid, "message": "study more", "when": "2030-01-02T07:00", "repeat": "none"})
    assert core.reminders.get(rid).message == "study more"
    c.post("/reminders", data={"csrf": t, "action": "delete", "id": rid})
    assert core.reminders.list() == []
    c.post("/memory", data={"csrf": t, "action": "delete_all", "pin": "9999"})
    assert len(core.memory.list_notes()) == 1                                 # wrong PIN: kept
    c.post("/memory", data={"csrf": t, "action": "delete_all", "pin": "4321"})
    assert core.memory.list_notes() == []


def test_default_bind_is_loopback_and_captures_off_by_default(cfg, tmp_path):
    assert cfg["webapp"]["host"] == "127.0.0.1"
    from sensebook.captures import CaptureStore
    s = CaptureStore(cfg)
    assert s.save("page", b"x", "jpg") is None
    cfg["storage"]["keep_captures"] = True
    s = CaptureStore(cfg)
    assert s.save("page", b"x", "jpg").exists() and s.purge() == 1


def test_gemini_error_redaction(monkeypatch):
    from sensebook.providers.gemini import redact
    monkeypatch.setenv("GEMINI_API_KEY", "SECRETKEY123")
    assert "SECRETKEY123" not in redact("failed SECRETKEY123 url?key=abc&x=1")
    assert "AIzaSyA1234567890123456789012" not in redact("AIzaSyA1234567890123456789012")
