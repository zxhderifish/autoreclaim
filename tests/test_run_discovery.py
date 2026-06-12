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


def _write_basics(tmp_path, settlements_rows):
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"keywords": ["amazon"]}))
    settlements = tmp_path / "settlements.json"
    settlements.write_text(json.dumps(settlements_rows))
    return profile, settlements, tmp_path / "queue.jsonl"


def test_discover_reports_unreachable_sources_in_email(tmp_path):
    profile, settlements, queue_path = _write_basics(tmp_path, [
        {"id": "", "source": "classaction.org", "title": "Amazon Prime Settlement",
         "category_tags": ["amazon"], "claim_url": "https://x/claim", "needs_proof": False},
    ])
    sites = tmp_path / "sites.json"
    sites.write_text(json.dumps({"classaction.org": "some text", "topclassactions.com": ""}))

    email = discover(settlements_path=settlements, profile_path=profile,
                     queue_path=queue_path, sites_path=sites)

    assert "Amazon Prime Settlement" in email
    assert "unreachable" in email
    assert "topclassactions.com" in email


def test_discover_reports_unreachable_sources_even_with_no_new_finds(tmp_path):
    profile, settlements, queue_path = _write_basics(tmp_path, [])
    sites = tmp_path / "sites.json"
    sites.write_text(json.dumps({"classaction.org": "", "openclassactions.com": "ok"}))

    email = discover(settlements_path=settlements, profile_path=profile,
                     queue_path=queue_path, sites_path=sites)

    assert "unreachable" in email
    assert "classaction.org" in email


def test_discover_stays_silent_when_no_finds_and_all_sources_healthy(tmp_path):
    profile, settlements, queue_path = _write_basics(tmp_path, [])
    sites = tmp_path / "sites.json"
    sites.write_text(json.dumps({"classaction.org": "ok"}))

    email = discover(settlements_path=settlements, profile_path=profile,
                     queue_path=queue_path, sites_path=sites)

    assert email == ""


def test_discover_reminds_about_unactioned_items_near_deadline(tmp_path):
    from datetime import date, timedelta
    profile, settlements, queue_path = _write_basics(tmp_path, [])
    soon = (date.today() + timedelta(days=5)).isoformat()
    far = (date.today() + timedelta(days=60)).isoformat()
    past = (date.today() - timedelta(days=3)).isoformat()
    rows = [
        {"id": "a", "title": "BofA ATM Fees", "status": "needs_human",
         "deadline": soon, "claim_url": "https://bofa/claim",
         "status_note": "needs Class Member ID"},
        {"id": "b", "title": "Far Future", "status": "needs_human", "deadline": far},
        {"id": "c", "title": "Already Filed", "status": "submitted", "deadline": soon},
        {"id": "d", "title": "Expired", "status": "needs_human", "deadline": past},
    ]
    queue_path.write_text("\n".join(json.dumps(r) for r in rows) + "\n")

    email = discover(settlements_path=settlements, profile_path=profile, queue_path=queue_path)

    assert "BofA ATM Fees" in email
    assert "https://bofa/claim" in email
    assert "needs Class Member ID" in email
    assert "Far Future" not in email
    assert "Already Filed" not in email
    assert "Expired" not in email


def test_discover_reminders_do_not_duplicate_new_finds(tmp_path):
    from datetime import date, timedelta
    soon = (date.today() + timedelta(days=5)).isoformat()
    profile, settlements, queue_path = _write_basics(tmp_path, [
        {"id": "", "source": "classaction.org", "title": "Amazon Prime Settlement",
         "category_tags": ["amazon"], "claim_url": "https://x/claim",
         "needs_proof": False, "deadline": soon},
    ])

    email = discover(settlements_path=settlements, profile_path=profile, queue_path=queue_path)

    assert email.count("Amazon Prime Settlement") == 1
