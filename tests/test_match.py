from autoreclaim.models import Settlement, make_id
from autoreclaim.match import load_profile, score


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
