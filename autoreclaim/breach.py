from __future__ import annotations

import re

# XposedOrNot — free, no API key. Returns the breaches an email appears in.
# Docs: https://xposedornot.com/api_doc  (rate limit 2 req/s)
API = "https://api.xposedornot.com/v1/check-email/{email}"

_TOKEN = re.compile(r"[a-z0-9]+")

# Drop generic words + breach-collection labels (not company names), so only real
# company names (Disqus, Lifeboat…) become match keywords.
_STOP = {
    "com", "net", "org", "inc", "llc", "ltd", "co", "the", "of", "and",
    "data", "breach", "settlement", "class", "action",
    "corp", "corporation", "company", "group", "incorporated", "limited",
    "collection", "combo", "combolist", "records", "billion", "million",
    "alleged", "public", "anti", "exploit", "leet", "dump", "leak", "list",
}


def _default_client():
    import requests
    return requests.Session()


def fetch_breaches(email: str, client=None) -> list[str]:
    """Breach/site names an email appears in (XposedOrNot, free, no key). [] if none."""
    client = client or _default_client()
    resp = client.get(API.format(email=email), timeout=20)
    if resp.status_code != 200:
        return []
    data = resp.json()
    breaches = data.get("breaches")
    if not breaches:
        return []  # {"Error": "Not found"} or empty
    flat = breaches[0] if isinstance(breaches[0], list) else breaches
    return [str(b) for b in flat]


# Substrings that mark a breach-collection label rather than a company name.
_COLLECTION_MARKERS = ("combo", "records", "billion", "million", "collection",
                       "antipublic", "exploit", "dump", "leak")


def breach_keywords(breaches: list[str]) -> list[str]:
    """Company-ish tokens from breach names, for matching data-breach settlements.

    Drops generic collection labels (Collection-1, AntiPublicCombo, 1.4BillionRecords…)
    and pure numbers, so only real company names become match keywords. De-dups in order.
    """
    seen, out = set(), []
    for name in breaches:
        for tok in _TOKEN.findall(name.lower()):
            if len(tok) < 3 or tok.isdigit() or tok in _STOP:
                continue
            if any(m in tok for m in _COLLECTION_MARKERS):
                continue
            if tok not in seen:
                seen.add(tok)
                out.append(tok)
    return out


def collect_breaches(emails, client=None) -> list[str]:
    """Merge breach/site names across MANY emails (people have several), deduped in order."""
    client = client or _default_client()
    seen, out = set(), []
    for email in emails:
        for name in fetch_breaches(email, client=client):
            if name not in seen:
                seen.add(name)
                out.append(name)
    return out


def main() -> None:
    """Print company keywords from breaches across the user's emails.

    Usage:
      python -m autoreclaim.breach a@x.com b@y.com   # scan the given emails
      python -m autoreclaim.breach                    # scan every email in profile.json
    """
    import json
    import sys

    emails = sys.argv[1:]
    if not emails:
        from pathlib import Path
        from .config import data_dir
        from .match import profile_emails
        p = data_dir() / "profile.json"
        emails = profile_emails(json.loads(p.read_text())) if p.exists() else []
    print(json.dumps(breach_keywords(collect_breaches(emails))))


if __name__ == "__main__":
    main()
