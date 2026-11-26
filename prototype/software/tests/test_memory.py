import json

from sensebook.memory import Memory


def test_memory_is_off_by_default_and_refuses_personal_writes(db):
    m = Memory(db)
    assert not m.enabled
    assert m.add_note("x") is None and m.add_bookmark("b", 1, "l") is None
    m.add_quiz_result(question="q", score=1.0)
    assert m.list_notes() == [] and m.quiz_history() == []


def test_crud_export_and_delete(db):
    m = Memory(db)
    m.set_enabled(True)
    nid = m.add_note("the mitochondria is the powerhouse")
    m.add_note("exam on friday")
    m.add_bookmark("Bio", 3, "cell page")
    m.add_quiz_result(quiz_id="q1", question="Q", score=0.5, feedback="f")
    assert m.relevant_notes("what is the mitochondria")[0].startswith("the mito")
    ex = json.loads(m.export_json())
    assert len(ex["notes"]) == 2 and len(ex["bookmarks"]) == 1 and len(ex["quiz_results"]) == 1
    assert "pin_hash" not in ex["profile"]
    assert m.delete_note(nid) and len(m.list_notes()) == 1
    assert m.delete_note_matching("friday") == 1
    m.delete_everything()
    ex = json.loads(m.export_json())
    assert all(ex[t] == [] for t in ("notes", "bookmarks", "quiz_results", "concepts", "sessions", "reminders"))


def test_pin_hashing_and_check(db):
    m = Memory(db)
    assert not m.pin_is_set()
    m.set_pin("2468")
    assert m.pin_is_set() and m.check_pin("2468") and not m.check_pin("0000")
    assert "2468" not in db.one("SELECT value v FROM profile WHERE key='pin_hash'")["v"]
    import pytest
    with pytest.raises(ValueError):
        m.set_pin("12")
