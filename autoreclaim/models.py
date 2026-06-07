from __future__ import annotations

import hashlib
import re
from dataclasses import dataclass, field, asdict

_WS = re.compile(r"\s+")


def normalize_title(title: str) -> str:
    """Lowercase, collapse whitespace — used for stable ids and dedupe keys."""
    return _WS.sub(" ", title.strip().lower())


def make_id(title: str) -> str:
    return hashlib.sha256(normalize_title(title).encode()).hexdigest()[:16]


@dataclass
class Settlement:
    id: str
    source: str
    title: str
    category_tags: list[str] = field(default_factory=list)
    deadline: str | None = None
    claim_url: str | None = None
    needs_proof: bool = False
    attestation_strength: str = "normal"  # normal | strict | unknown
    est_payout: str | None = None

    def to_dict(self) -> dict:
        return asdict(self)

    @classmethod
    def from_dict(cls, d: dict) -> "Settlement":
        known = {f for f in cls.__dataclass_fields__}
        return cls(**{k: v for k, v in d.items() if k in known})
