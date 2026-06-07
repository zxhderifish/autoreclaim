from autoreclaim.models import Settlement, make_id
from autoreclaim.dedupe import dedupe


def _s(title, source, **kw):
    return Settlement(id=make_id(title), source=source, title=title, **kw)


def test_collapses_same_title_across_sources():
    a = _s("Acme Data Breach", "topclassactions.com", claim_url=None)
    b = _s("acme  data breach", "claimdepot.com", claim_url="https://x/claim")
    out = dedupe([a, b])
    assert len(out) == 1
    # the merged record keeps the non-null claim_url
    assert out[0].claim_url == "https://x/claim"


def test_keeps_distinct_settlements():
    a = _s("Acme Breach", "topclassactions.com")
    b = _s("Globex Refund", "claimdepot.com")
    assert len(dedupe([a, b])) == 2
