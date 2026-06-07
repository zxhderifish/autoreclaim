import json
from autoreclaim.models import Settlement, make_id
from autoreclaim.pipeline import run_pipeline


def _settlement_dict(title, tags, **extra):
    d = Settlement(id=make_id(title), source="topclassactions.com",
                   title=title, category_tags=tags).to_dict()
    d.update(extra)
    return d


def test_keyword_fallback_when_not_agent_judged(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"keywords": ["amazon"]}))
    parsed = [
        _settlement_dict("Amazon Prime Settlement", ["amazon"]),
        _settlement_dict("amazon  prime settlement", ["retail"]),  # dup of above
        _settlement_dict("Globex Paint Recall", ["paint"]),        # no match -> dropped
    ]
    queue, new_pending = run_pipeline(parsed, profile_path=profile, existing_queue=[])
    assert len(queue) == 1                          # deduped + only matched kept
    assert queue[0]["status"] == "pending_confirm"
    assert queue[0]["match_reason"] == "amazon"
    assert queue[0]["confidence"] == "low"          # keyword-only is weak evidence
    assert len(new_pending) == 1


def test_agent_judgment_takes_priority_over_keywords(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"keywords": []}))   # no keyword would ever match
    parsed = [
        _settlement_dict("Chase Overdraft Fee Settlement", ["banking"],
                         eligible=True,
                         eligibility_reason="You bank with Chase",
                         confidence="high"),
        _settlement_dict("Globex Paint Recall", ["paint"], eligible=False),  # agent said no
    ]
    queue, new_pending = run_pipeline(parsed, profile_path=profile, existing_queue=[])
    assert len(queue) == 1
    assert queue[0]["title"] == "Chase Overdraft Fee Settlement"
    assert queue[0]["match_reason"] == "You bank with Chase"
    assert queue[0]["confidence"] == "high"
    assert len(new_pending) == 1


def test_pipeline_does_not_re_notify_already_known(tmp_path):
    profile = tmp_path / "profile.json"
    profile.write_text(json.dumps({"keywords": ["amazon"]}))
    parsed = [_settlement_dict("Amazon Prime Settlement", ["amazon"])]
    existing_id = make_id("Amazon Prime Settlement")
    existing = [{"id": existing_id, "status": "submitted", "title": "Amazon Prime Settlement"}]
    queue, new_pending = run_pipeline(parsed, profile_path=profile, existing_queue=existing)
    assert len(queue) == 1
    assert queue[0]["status"] == "submitted"     # preserved
    assert new_pending == []                      # already known -> no email row
