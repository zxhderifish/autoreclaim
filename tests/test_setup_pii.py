from onboarding.setup_pii import validate_pii


def test_flags_empty_and_placeholder_fields():
    data = {"full_name": "test", "address_line1": "", "city": "Sunnyvale",
            "state": "CA", "zip": "94085", "email": "real@x.com", "phone": "111-111-1111"}
    bad = validate_pii(data)
    assert "full_name" in bad       # "test" placeholder
    assert "address_line1" in bad   # empty
    assert "phone" in bad           # 111-111-1111
    assert "city" not in bad
    assert "email" not in bad


def test_clean_pii_passes():
    data = {"full_name": "Jane Doe", "address_line1": "1 Main St", "city": "SF",
            "state": "CA", "zip": "94016", "email": "jane@x.com", "phone": "415-555-1234"}
    assert validate_pii(data) == []
