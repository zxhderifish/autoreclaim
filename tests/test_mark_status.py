import json
import pytest
from autoreclaim.mark_status import mark


def test_mark_sets_status_and_timestamp(tmp_path):
    qp = tmp_path / "queue.jsonl"
    qp.write_text(json.dumps({"id": "a", "status": "pending_confirm", "submitted_at": None}) + "\n")

    mark("a", "submitted", queue_path=qp)

    row = json.loads(qp.read_text().splitlines()[0])
    assert row["status"] == "submitted"
    assert row["submitted_at"] is not None


def test_mark_unknown_id_raises(tmp_path):
    qp = tmp_path / "queue.jsonl"
    qp.write_text(json.dumps({"id": "a", "status": "pending_confirm"}) + "\n")
    with pytest.raises(KeyError):
        mark("zzz", "submitted", queue_path=qp)
