from autoreclaim.queue import load_queue, save_queue, upsert


def test_save_then_load_roundtrip(tmp_path):
    p = tmp_path / "queue.jsonl"
    items = [{"id": "a", "status": "pending_confirm"}, {"id": "b", "status": "submitted"}]
    save_queue(p, items)
    assert load_queue(p) == items


def test_load_missing_file_returns_empty(tmp_path):
    assert load_queue(tmp_path / "nope.jsonl") == []


def test_upsert_adds_new_item():
    existing = [{"id": "a", "status": "pending_confirm"}]
    out = upsert(existing, {"id": "b", "status": "pending_confirm"})
    assert {i["id"] for i in out} == {"a", "b"}


def test_upsert_preserves_existing_status_for_known_id():
    # 'a' was already submitted; a re-discovery must NOT reset it to pending
    existing = [{"id": "a", "status": "submitted", "match_score": 3}]
    out = upsert(existing, {"id": "a", "status": "pending_confirm", "match_score": 9})
    a = [i for i in out if i["id"] == "a"][0]
    assert a["status"] == "submitted"      # status preserved
    assert a["match_score"] == 9           # other fields refreshed
    assert len(out) == 1                   # no duplicate row
