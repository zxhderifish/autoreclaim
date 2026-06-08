from autoreclaim.breach import fetch_breaches, breach_keywords, collect_breaches


class _Resp:
    def __init__(self, status, data):
        self.status_code = status
        self._data = data

    def json(self):
        return self._data


class _Client:
    def __init__(self, resp):
        self._resp = resp
        self.calls = []

    def get(self, url, timeout=0):
        self.calls.append(url)
        return self._resp


class _MultiClient:
    """Maps email-in-url -> response, so multiple emails return different breaches."""
    def __init__(self, by_email):
        self._by_email = by_email
        self.calls = []

    def get(self, url, timeout=0):
        self.calls.append(url)
        for email, resp in self._by_email.items():
            if email in url:
                return resp
        return _Resp(200, {"Error": "Not found"})


def test_fetch_breaches_extracts_names():
    data = {"breaches": [["Disqus", "Lifeboat", "Collection-1"]], "status": "success"}
    out = fetch_breaches("a@b.com", client=_Client(_Resp(200, data)))
    assert out == ["Disqus", "Lifeboat", "Collection-1"]


def test_fetch_breaches_not_found_returns_empty():
    c = _Client(_Resp(200, {"Error": "Not found", "email": None}))
    assert fetch_breaches("a@b.com", client=c) == []


def test_breach_keywords_keeps_companies_drops_collections_and_numbers():
    kws = breach_keywords(["Disqus", "Lifeboat", "Collection-1", "AntiPublicCombo",
                           "1.4BillionRecords", "ExploitIN"])
    assert "disqus" in kws
    assert "lifeboat" in kws
    assert "collection" not in kws        # generic collection label
    assert "antipubliccombo" not in kws   # collection label (substring marker)
    assert "4billionrecords" not in kws
    assert "exploitin" not in kws
    assert "1" not in kws                  # pure number dropped


def test_breach_keywords_empty_for_no_breaches():
    assert breach_keywords([]) == []


def test_collect_breaches_merges_and_dedupes_across_emails():
    client = _MultiClient({
        "a@x.com": _Resp(200, {"breaches": [["Disqus", "Lifeboat"]]}),
        "b@y.com": _Resp(200, {"breaches": [["Lifeboat", "Dropbox"]]}),  # Lifeboat overlaps
    })
    out = collect_breaches(["a@x.com", "b@y.com"], client=client)
    assert out == ["Disqus", "Lifeboat", "Dropbox"]  # merged, order-preserving, deduped


def test_collect_breaches_handles_email_with_no_breaches():
    client = _MultiClient({"a@x.com": _Resp(200, {"breaches": [["Disqus"]]})})
    out = collect_breaches(["a@x.com", "clean@nowhere.com"], client=client)
    assert out == ["Disqus"]


def test_collect_breaches_empty_for_no_emails():
    assert collect_breaches([], client=_MultiClient({})) == []
