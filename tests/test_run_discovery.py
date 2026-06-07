import json
from autoreclaim.run_discovery import discover
from autoreclaim.models import make_id


def test_discover_updates_queue_file_and_returns_email(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"keywords": ["amazon"]}))
    queue_path = tmp_path / "queue.jsonl"

    settlements = tmp_path / "settlements.json"
    settlements.write_text(json.dumps([
        {"id": "", "source": "topclassactions.com", "title": "Amazon Prime Settlement",
         "category_tags": ["amazon"], "claim_url": "https://x/claim", "needs_proof": False},
    ]))

    email = discover(settlements_path=settlements, profile_path=profile, queue_path=queue_path)

    saved = [json.loads(l) for l in queue_path.read_text().splitlines() if l.strip()]
    assert len(saved) == 1
    assert saved[0]["id"] == make_id("Amazon Prime Settlement")
    assert "Amazon Prime Settlement" in email
