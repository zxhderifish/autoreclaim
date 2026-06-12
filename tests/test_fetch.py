from autoreclaim.fetch import SOURCES, fetch_all


class _FakeResp:
    def __init__(self, text):
        self.text = text
        self.status_code = 200

    def raise_for_status(self):
        pass


class _FakeClient:
    def __init__(self):
        self.calls = []

    def get(self, url, timeout=0):
        self.calls.append(url)
        return _FakeResp(f"<html>{url}</html>")


def test_sources_are_the_six_aggregators():
    assert len(SOURCES) == 6
    assert "topclassactions.com" in SOURCES


def test_fetch_all_hits_every_source_and_keys_by_domain():
    client = _FakeClient()
    out = fetch_all(client=client)
    assert set(out.keys()) == set(SOURCES.keys())
    assert out["topclassactions.com"]
    assert len(client.calls) == 6


class _FlakyClient:
    """Fails for one domain, succeeds for the rest."""

    def __init__(self, bad_domain):
        self.bad_domain = bad_domain

    def get(self, url, timeout=0):
        if self.bad_domain in url:
            raise ConnectionError("boom")
        return _FakeResp(f"<html>{url}</html>")


def test_fetch_all_warns_on_stderr_when_a_source_fails(capsys):
    out = fetch_all(client=_FlakyClient("topclassactions.com"), curl_fetch=lambda url: "")
    assert out["topclassactions.com"] == ""
    err = capsys.readouterr().err
    assert "topclassactions.com" in err
    assert "WARN" in err


def test_fetch_all_recovers_via_curl_when_requests_is_blocked(capsys):
    out = fetch_all(
        client=_FlakyClient("topclassactions.com"),
        curl_fetch=lambda url: "<html>curl got it</html>",
    )
    assert out["topclassactions.com"] == "<html>curl got it</html>"
    err = capsys.readouterr().err
    assert "recovered via curl" in err
