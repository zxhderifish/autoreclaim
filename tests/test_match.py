from autoreclaim.models import Settlement, make_id
from autoreclaim.match import load_profile, score, profile_emails


def _profile(tmp_path, keywords):
    import json
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({"keywords": keywords}))
    return load_profile(p)


def _s(title, tags=None):
    return Settlement(id=make_id(title), source="x", title=title, category_tags=tags or [])


def test_matches_keyword_in_title(tmp_path):
    prof = _profile(tmp_path, ["amazon", "chase"])
    sc, reasons = score(_s("Amazon Prime Pricing Settlement"), prof)
    assert sc == 1
    assert reasons == ["amazon"]


def test_matches_keyword_in_category_tags(tmp_path):
    prof = _profile(tmp_path, ["verizon"])
    sc, reasons = score(_s("Carrier Overcharge Settlement", tags=["verizon", "telecom"]), prof)
    assert sc == 1
    assert reasons == ["verizon"]


def test_no_match_scores_zero(tmp_path):
    prof = _profile(tmp_path, ["amazon"])
    sc, reasons = score(_s("Globex Paint Recall"), prof)
    assert sc == 0
    assert reasons == []


def test_substring_does_not_falsely_match(tmp_path):
    # "att" (carrier) must not match the word "battery"
    prof = _profile(tmp_path, ["att"])
    sc, _ = score(_s("Battery Defect Settlement"), prof)
    assert sc == 0


def test_load_profile_reads_common_pack_lowercased(tmp_path):
    import json
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({"keywords": ["Chase"], "common_pack": ["Amazon", "Google"]}))
    prof = load_profile(p)
    assert prof["keywords"] == ["chase"]
    assert prof["common_pack"] == ["amazon", "google"]


def test_load_profile_common_pack_defaults_empty(tmp_path):
    import json
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({"keywords": ["chase"]}))
    assert load_profile(p)["common_pack"] == []


def test_profile_emails_reads_list():
    prof = {"emails": ["A@X.com", "b@y.com"]}
    assert profile_emails(prof) == ["a@x.com", "b@y.com"]


def test_profile_emails_accepts_single_email_alias():
    # backward-compat: old profiles used a single "email" string
    assert profile_emails({"email": "Me@Example.com"}) == ["me@example.com"]


def test_profile_emails_dedupes_and_drops_blanks():
    prof = {"emails": ["a@x.com", "  ", "A@X.com", "b@y.com"]}
    assert profile_emails(prof) == ["a@x.com", "b@y.com"]


def test_profile_emails_empty_when_none():
    assert profile_emails({"keywords": ["chase"]}) == []


def test_load_profile_passes_through_state_lowercased(tmp_path):
    import json
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({"keywords": ["amazon"], "state": "WA"}))
    assert load_profile(p)["state"] == "wa"


def test_load_profile_state_defaults_to_empty_string(tmp_path):
    import json
    p = tmp_path / "profile.json"
    p.write_text(json.dumps({"keywords": ["amazon"]}))
    assert load_profile(p)["state"] == ""
