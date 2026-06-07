from autoreclaim.models import Settlement, make_id


def test_make_id_is_stable_and_source_independent():
    a = make_id("Acme Data Breach Settlement")
    b = make_id("  acme   data breach settlement  ")  # spacing/case differ
    assert a == b
    assert len(a) == 16


def test_settlement_roundtrips_through_dict():
    s = Settlement(
        id=make_id("Acme Data Breach"),
        source="topclassactions.com",
        title="Acme Data Breach",
        category_tags=["data_breach"],
        deadline="2026-09-01",
        claim_url="https://example.com/claim",
        needs_proof=False,
        attestation_strength="normal",
        est_payout="$25",
    )
    d = s.to_dict()
    assert d["id"] == s.id
    assert Settlement.from_dict(d) == s
