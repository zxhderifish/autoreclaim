from autoreclaim.gmail_brands import sender_domains_to_keywords, new_brands


def test_extracts_brand_from_email_sender():
    assert sender_domains_to_keywords(["no-reply@email.chase.com"]) == ["chase"]


def test_strips_subdomains_to_registrable_label():
    assert sender_domains_to_keywords(["marketing.amazon.com"]) == ["amazon"]


def test_handles_bare_domain_and_email_alike():
    assert sender_domains_to_keywords(["uber.com", "receipts@uber.com"]) == ["uber"]


def test_drops_public_mailbox_providers():
    senders = ["friend@gmail.com", "me@outlook.com", "x@yahoo.com", "y@icloud.com"]
    assert sender_domains_to_keywords(senders) == []


def test_handles_multi_label_tld():
    assert sender_domains_to_keywords(["orders@tesco.co.uk"]) == ["tesco"]


def test_dedupes_preserving_order():
    senders = ["a@chase.com", "alerts@email.chase.com", "b@amazon.com"]
    assert sender_domains_to_keywords(senders) == ["chase", "amazon"]


def test_ignores_blank_and_malformed():
    assert sender_domains_to_keywords(["", "  ", "not-an-email"]) == []


def test_new_brands_returns_only_unseen():
    found = ["amazon", "chase", "peloton"]
    existing = ["amazon", "netflix"]
    assert new_brands(found, existing) == ["chase", "peloton"]


def test_new_brands_is_case_insensitive_and_deduped():
    found = ["Chase", "chase", "Peloton"]
    existing = ["AMAZON"]
    assert new_brands(found, existing) == ["chase", "peloton"]


def test_new_brands_empty_when_all_known():
    assert new_brands(["amazon"], ["amazon", "chase"]) == []
