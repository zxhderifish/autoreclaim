from autoreclaim.notify import render_email


def test_empty_pending_renders_silent_marker():
    assert render_email([]) == ""   # empty body -> agent sends nothing


def test_renders_one_line_per_pending_with_reason_confidence_and_link():
    pending = [{
        "title": "Amazon Prime Settlement",
        "match_reason": "You shop at Amazon",
        "confidence": "high",
        "est_payout": "$25",
        "deadline": "2026-09-01",
        "claim_url": "https://x/claim",
        "needs_proof": False,
    }]
    body = render_email(pending)
    assert "Amazon Prime Settlement" in body
    assert "You shop at Amazon" in body       # human-readable agent reason
    assert "high" in body                     # confidence shown
    assert "$25" in body
    assert "2026-09-01" in body
    assert "https://x/claim" in body
    assert "AutoReclaim" in body
    assert "/autoreclaim-confirm" in body


def test_null_claim_url_shows_placeholder_not_none():
    body = render_email([{"title": "X", "match_reason": "", "claim_url": None}])
    assert "(no link)" in body
    assert "None" not in body
