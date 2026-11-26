import sys
from datetime import datetime, timedelta, timezone
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from sensebook.app import SenseBookApp  # noqa: E402
from sensebook.audio import NullBackend, OfflineSpeech, Player, ScriptedRecorder  # noqa: E402
from sensebook.camera import ScriptedCamera  # noqa: E402
from sensebook.config import load_config  # noqa: E402
from sensebook.db import Database  # noqa: E402
from sensebook.hardware import NullHardware  # noqa: E402
from sensebook.providers.mock import MockSpeech, MockTutor, MockVision  # noqa: E402


class FakeClock:
    def __init__(self, start=None):
        self.now = start or datetime(2026, 11, 26, 10, 0, tzinfo=timezone.utc)   # 16:00 in Dhaka

    def __call__(self):
        return self.now

    def advance(self, **kw):
        self.now += timedelta(**kw)


class NoOffline(OfflineSpeech):
    def available(self):
        return False


@pytest.fixture
def clock():
    return FakeClock()


@pytest.fixture
def cfg(tmp_path):
    return load_config("nonexistent.yaml", {"data_dir": str(tmp_path)})


@pytest.fixture
def db():
    return Database(":memory:")


@pytest.fixture
def make_app(cfg, clock):
    def make(camera=True):
        speech, logs = MockSpeech(), []
        app = SenseBookApp(cfg, MockVision(), MockTutor(), speech, ScriptedCamera() if camera else None,
                           NullHardware(log=lambda *a: None), ScriptedRecorder(), Player(NullBackend()),
                           db=Database(":memory:"), clock=clock, log=lambda *a: logs.append(" ".join(map(str, a))), offline=NoOffline())
        app.logs = logs
        app.memory.set("language", "en")
        app.speech_log = speech.log
        return app
    return make
