import threading
import time

from sensebook.providers.base import AudioClip, ProviderUnavailable
from sensebook.providers.mock import MockVision


def wait(pred, t=3.0):
    end = time.time() + t
    while time.time() < end:
        if pred():
            return True
        time.sleep(0.01)
    return False


def roles(app):
    return [r for r, _ in app.speech_log]


def test_end_to_end_mock_session(make_app, clock):
    app = make_app()
    app.memory.set_enabled(True)
    app.memory.set_pin("1234")
    MockVision.calls = 0

    # 1. capture -> cloud read -> cache; LED is lit during the vision call
    seen = []
    orig = app.vision.read_page
    app.vision.read_page = lambda j, l: (seen.append(app.hw.led_on), orig(j, l))[1]
    app.on_page_settled()
    assert app.spread and len(app.spread.pages) == 2 and MockVision.calls == 2
    assert seen == [True, True] and app.hw.led_on is False
    app.on_page_settled()                                   # same page again: served from cache, no cloud
    assert MockVision.calls == 2 and all(p.from_cache for p in app.spread.pages)
    assert len(app.cache.library()) == 2

    # 2. faithful reading in the reader voice
    app.start_reading()
    assert wait(lambda: app.read_idx >= len(app.spread.units) and not app._reading)
    reader_lines = [t for r, t in app.speech_log if r == "reader"]
    assert reader_lines and reader_lines[0] == app.spread.units[0][2]

    # 3. Ask: grounded answer in explainer voice; off-page question says so
    key = app.spread.pages[0].blocks[1].text.split()[0].strip(".,")
    n = len(app.speech_log)
    app.on_utterance(AudioClip(b"", f"explain {key} please"))
    assert app.speech_log[n][0] == "explainer" and "The page says" in app.speech_log[n][1]
    app.on_utterance(AudioClip(b"", "who won the 1971 cricket final"))
    assert any("not on this page" in t for _, t in app.speech_log[-3:])

    # 4. quiz by voice command; answers come through the same Ask path
    app.mode = "idle"
    t = threading.Thread(target=app.start_quiz)
    t.start()
    assert wait(lambda: app.mode == "quiz")
    for a in ["a", "a", "a", "something", "something"]:
        app.on_utterance(AudioClip(b"", a))          # answers arrive through the normal Ask path
    t.join(5)
    assert not t.is_alive()
    assert len(app.memory.quiz_history()) == 5 and app.mode == "idle"
    assert app.db.one("SELECT COUNT(*) c FROM concepts")["c"] >= 1

    # 5. reminder by voice -> structured -> persisted -> fires -> spoken -> snooze via play/pause
    app.on_utterance(AudioClip(b"", "remind me to revise chapter 3 tomorrow at 7 pm"))
    rs = app.reminders.list()
    assert len(rs) == 1 and rs[0].message.startswith("revise chapter 3")
    clock.advance(days=1, hours=4)
    app.scheduler.tick()
    ev = app.hw.events.get_nowait()
    assert ev == f"reminder:{rs[0].id}"
    app.handle(ev)
    assert "Reminder: revise chapter 3" in app.speech_log[-1][1]
    app.handle("play_pause")                                # snooze
    assert app.reminders.get(rs[0].id).active and app.reminders.get(rs[0].id).next_fire > clock()


def test_chime_precedes_explanation_but_not_reading(make_app):
    app = make_app()
    played = []
    orig = app.player.play
    app.player.play = lambda wav: (played.append(len(wav)), orig(wav))[1]
    from sensebook.audio import chime_wav
    n_chime = len(chime_wav())
    app.say("AI explains", "explainer")
    assert played[0] == n_chime
    played.clear()
    app.say("Printed text", "reader")
    assert played[0] != n_chime and len(played) == 1


def test_mic_mute_hard_blocks_recording(make_app):
    app = make_app()
    app.recorder.say("hello")
    app.hw.set_mic_muted(True)
    app.ask_start()
    assert not app.recording and not app.recorder.active
    assert "Microphone off" in app.speech_log[-1][1]


def test_offline_cached_pages_readable_new_pages_spoken_message(make_app):
    app = make_app()
    app.on_page_settled()
    cached_first = app.spread.units[0][2]

    def boom(*a):
        raise ProviderUnavailable("down")
    app.vision.read_page = boom
    app.on_page_settled()                                    # same page: cache hit, works offline
    assert app.spread.units[0][2] == cached_first
    app.camera.turn_to(1)
    app.on_page_settled()                                    # new page: friendly spoken message
    assert any("No internet" in t for _, t in app.speech_log)


def test_camera_blocked_and_unclear_messages(make_app):
    app = make_app()
    app.camera.blocked = True
    app.on_page_settled()
    assert "camera looks covered" in app.speech_log[-1][1]
    app.camera.blocked = False
    app.camera.pages[0][:] = 120                             # flat grey: no detail
    app.on_page_settled()
    assert "hold the book flatter" in app.speech_log[-1][1]


def test_navigation_back_forward_and_low_confidence(make_app, monkeypatch):
    app = make_app()
    app.on_page_settled()
    app._reading = False
    app.read_idx = 3
    app.jump(+1) if False else None
    with app._read_lock:
        app.read_idx = 3
    app.spread.units  # sanity
    app._reading = True                                      # pretend reading so jump does not start a thread
    app.jump(-1)
    assert app.read_idx == 2
    app.jump(+1)
    assert app.read_idx == 3
    app._reading = False
    # a low-confidence page is never read or cached
    app2 = make_app()
    app2.vision.read_page = lambda j, l: type(MockVision().read_page(j, l))(
        MockVision().read_page(j, l).blocks, "en", 0.2)
    app2.on_page_settled()
    assert app2.spread is None and app2.cache.library() == []
    assert any("small print" in t for _, t in app2.speech_log)               # asks to pull the stick up first
    app2.on_page_settled()                                                    # after the view changed: full-res try, still doubtful
    assert app2.spread is None and app2.cache.library() == []
    assert any("not sure" in t for _, t in app2.speech_log)


def test_discussion_plays_and_interruption_gets_hosts_reply(make_app):
    app = make_app()
    app.on_page_settled()
    app.session_pages[:] = app.spread.pages
    app.start_discussion(1)
    assert wait(lambda: app.mode == "idle" and app._disc is None)
    assert {"learner", "teacher"} <= set(roles(app))
    # interruption path
    from sensebook.discussion import Discussion
    d = Discussion(app.tutor_p, app.speech, app.player, "en", 2)
    d.prepare(app.session_text())
    app._disc, app.mode = d, "discussion"
    n = len(app.speech_log)
    app.on_utterance(AudioClip(b"", "what is that"))
    new = app.speech_log[n:]
    assert any("Good question: what is that" in t for _, t in new)


def test_spoken_delete_everything_needs_forward_button_confirmation(make_app):
    app = make_app()
    app.memory.set_enabled(True)
    app.memory.add_note("secret")
    app.on_utterance(AudioClip(b"", "forget everything"))
    assert len(app.memory.list_notes()) == 1                 # nothing deleted yet
    app.handle("back")                                       # Back cancels
    assert len(app.memory.list_notes()) == 1
    app.on_utterance(AudioClip(b"", "forget everything"))
    app.handle("forward")                                    # Forward confirms
    assert app.memory.list_notes() == []
