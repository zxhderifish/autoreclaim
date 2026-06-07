from __future__ import annotations

from .models import Settlement, normalize_title


def _merge(a: Settlement, b: Settlement) -> Settlement:
    """Prefer existing non-null fields from a, fill gaps from b, union sources/tags."""
    merged = Settlement.from_dict(a.to_dict())
    for fld in ("deadline", "claim_url", "est_payout"):
        if getattr(merged, fld) is None and getattr(b, fld) is not None:
            setattr(merged, fld, getattr(b, fld))
    merged.category_tags = sorted(set(a.category_tags) | set(b.category_tags))
    sources = sorted(set(a.source.split(",")) | set(b.source.split(",")))
    merged.source = ",".join(sources)
    if merged.needs_proof or b.needs_proof:
        merged.needs_proof = True
    return merged


def dedupe(settlements: list[Settlement]) -> list[Settlement]:
    by_key: dict[str, Settlement] = {}
    for s in settlements:
        key = normalize_title(s.title)
        by_key[key] = _merge(by_key[key], s) if key in by_key else s
    return list(by_key.values())
