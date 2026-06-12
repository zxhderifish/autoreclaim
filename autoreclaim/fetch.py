from __future__ import annotations

# Domain -> the page that lists currently-open settlements.
SOURCES = {
    "topclassactions.com": "https://topclassactions.com/category/lawsuit-settlements/open-lawsuit-settlements/",
    "claimdepot.com": "https://www.claimdepot.com/settlements",
    "classaction.org": "https://www.classaction.org/settlements",
    "openclassactions.com": "https://openclassactions.com/",
    "consumer-action.org": "https://www.consumer-action.org/lawsuits/by-status/open",
    "fileyourclaim.co": "https://fileyourclaim.co/open-class-action-settlements",
}

_HEADERS = {"User-Agent": "Mozilla/5.0 (AutoReclaim research preview)"}


def _default_client():
    import requests
    s = requests.Session()
    s.headers.update(_HEADERS)
    return s


def _curl_fetch(url: str) -> str:
    """Fallback for sources that reject python-requests' TLS fingerprint
    (e.g. Cloudflare 403s requests but passes system curl). '' on failure."""
    import subprocess

    try:
        proc = subprocess.run(
            ["curl", "-sS", "--fail", "-L", "--max-time", "30",
             "-A", _HEADERS["User-Agent"], url],
            capture_output=True, text=True, timeout=45,
        )
        return proc.stdout if proc.returncode == 0 else ""
    except Exception:
        return ""


def fetch_all(client=None, curl_fetch=_curl_fetch) -> dict[str, str]:
    """Return {domain: raw_html}. A failed source maps to '' so others still proceed.

    Failures are warned on stderr (stdout stays clean for piped JSON)."""
    import sys

    client = client or _default_client()
    out: dict[str, str] = {}
    for domain, url in SOURCES.items():
        try:
            resp = client.get(url, timeout=30)
            resp.raise_for_status()
            out[domain] = resp.text
        except Exception as e:
            body = curl_fetch(url)
            out[domain] = body
            if body:
                print(f"WARN: {domain} blocked requests ({e}); recovered via curl", file=sys.stderr)
            else:
                print(f"WARN: {domain} fetch failed: {e}", file=sys.stderr)
    return out
