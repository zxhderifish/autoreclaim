from autoreclaim.breach import fetch_breaches, breach_keywords


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
