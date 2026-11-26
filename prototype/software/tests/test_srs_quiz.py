from sensebook.memory import Memory
from sensebook.providers.base import AudioClip
from sensebook.providers.mock import MockTutor
from sensebook.quiz import ConceptTracker, QuizSession, sm2


def test_sm2_progression_and_lapse():
    e, r, i = 2.5, 0, 0.0
    e, r, i = sm2(e, r, i, 5)
    assert (r, i) == (1, 1.0)
    e, r, i = sm2(e, r, i, 4)
    assert (r, i) == (2, 6.0)
    e, r, i = sm2(e, r, i, 4)
    assert r == 3 and i == round(6 * e_prev(2.5, 5, 4), 1) or i > 6
    e2, r2, i2 = sm2(e, r, i, 1)                       # lapse
    assert (r2, i2) == (0, 1.0) and e2 >= 1.3


def e_prev(e0, *qs):
    for q in qs:
        e0 = max(1.3, e0 + 0.1 - (5 - q) * (0.08 + (5 - q) * 0.02))
    return e0


def test_tracker_schedules_due_reviews(db, clock):
    m = Memory(db)
    t = ConceptTracker(db, m, clock)
    t.record("osmosis", 1.0)
    assert db.one("SELECT COUNT(*) c FROM concepts")["c"] == 0          # memory off: nothing stored
    m.set_enabled(True)
    t.record("osmosis", 1.0)
    assert t.due() == []
    clock.advance(days=1, minutes=1)
    assert [c["name"] for c in t.due()] == ["osmosis"]
    t.record("osmosis", 0.0)                                             # failed review => back to 1 day
    row = db.one("SELECT * FROM concepts")
    assert row["repetitions"] == 0 and row["interval_days"] == 1.0 and row["mastery"] < 1.0


class IO:
    def __init__(self, answers):
        self.answers, self.spoken = list(answers), []

    def speak(self, text, role="explainer"):
        self.spoken.append(text)

    def listen(self):
        a = self.answers.pop(0) if self.answers else None
        return None if a is None else AudioClip(b"", a)


def test_quiz_flow_with_mock_provider_grades_and_stores(db, clock):
    m = Memory(db)
    m.set_enabled(True)
    page = "Plants make food using sunlight. Chlorophyll absorbs light energy. Rain returns water to land."
    t = ConceptTracker(db, m, clock)
    io = IO(["a", "mercury", "a", "plants make food using sunlight", None])
    out = QuizSession(MockTutor(), m, t, io, "en").run(page)
    assert len(out.results) == 5
    scores = [r["score"] for r in out.results]
    assert scores[0] == 1.0 and scores[1] == 0.0 and scores[3] >= 0.5 and scores[4] == 0.0
    assert len(m.quiz_history()) == 5
    assert db.one("SELECT COUNT(*) c FROM concepts")["c"] >= 1
    assert any("scored" in s for s in io.spoken)
    assert any("Correct" in s for s in io.spoken) and any("Not quite" in s or "Partly" in s for s in io.spoken)
