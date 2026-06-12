from __future__ import annotations

import json
import re
from pathlib import Path

from .models import Settlement

_TOKEN = re.compile(r"[a-z0-9]+")


def load_profile(path) -> dict:
    data = json.loads(Path(path).read_text())
    return {
        "keywords": [k.strip().lower() for k in data.get("keywords", []) if k.strip()],
        # common_pack = broad "almost-everyone" defaults; kept separate so matching can
        # treat them conservatively (low confidence) vs the user's deliberate keywords.
        "common_pack": [k.strip().lower() for k in data.get("common_pack", []) if k.strip()],
        "emails": profile_emails(data),
        # Optional coarse location — lets matching include/exclude state-scoped
        # settlements (e.g. "Washington residents only"). Never street-level PII.
        "state": (data.get("state") or "").strip().lower(),
        # Brands the user has explicitly said don't apply to them (recorded by the
        # confirm flow) — a hard non-match, so they're never matched or asked again.
        "ruled_out": [k.strip().lower() for k in data.get("ruled_out", []) if k.strip()],
    }


def profile_emails(profile: dict) -> list[str]:
    """All of the user's emails, lowercased + deduped.

    Supports `emails: [...]` (preferred — people have several) and the older single
    `email: "..."` string for backward compatibility. Powers the data-breach scan.
    """
    raw = profile.get("emails")
    if isinstance(raw, list):
        vals = raw
    elif profile.get("email"):
        vals = [profile["email"]]
    else:
        vals = []
    seen, out = set(), []
    for e in vals:
        e = (e or "").strip().lower()
        if e and e not in seen:
            seen.add(e)
            out.append(e)
    return out


def score(settlement: Settlement, profile: dict) -> tuple[int, list[str]]:
    title_tokens = set(_TOKEN.findall(settlement.title.lower()))
    tag_tokens = {t.strip().lower() for t in settlement.category_tags}
    haystack = title_tokens | tag_tokens
    ruled_out = set(profile.get("ruled_out", []))
    reasons = [kw for kw in profile["keywords"] if kw in haystack and kw not in ruled_out]
    # de-dup while preserving order
    seen, ordered = set(), []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return len(ordered), ordered
