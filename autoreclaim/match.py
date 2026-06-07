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
    }


def score(settlement: Settlement, profile: dict) -> tuple[int, list[str]]:
    title_tokens = set(_TOKEN.findall(settlement.title.lower()))
    tag_tokens = {t.strip().lower() for t in settlement.category_tags}
    haystack = title_tokens | tag_tokens
    reasons = [kw for kw in profile["keywords"] if kw in haystack]
    # de-dup while preserving order
    seen, ordered = set(), []
    for r in reasons:
        if r not in seen:
            seen.add(r)
            ordered.append(r)
    return len(ordered), ordered
