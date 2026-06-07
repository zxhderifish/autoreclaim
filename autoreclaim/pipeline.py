from __future__ import annotations

from datetime import datetime, timezone

from .models import Settlement
from .match import load_profile, score
from .dedupe import dedupe
from .queue import upsert


def _now() -> str:
    return datetime.now(timezone.utc).isoformat()


def _eligibility(settlement: Settlement, judgment: dict, profile: dict):
    """Return (reason, confidence) if eligible, else (None, None).

    The routine agent's semantic judgment takes priority. Falls back to keyword
    matching only when a settlement wasn't agent-judged (e.g. local tests / no agent).
    """
    if "eligible" in judgment:
        if not judgment.get("eligible"):
            return None, None
        return (judgment.get("eligibility_reason") or "agent judged eligible",
                judgment.get("confidence") or "medium")
    # fallback: keyword match — weak evidence, kept for local/no-agent runs
    sc, reasons = score(settlement, profile)
    if sc == 0:
        return None, None
    return ", ".join(reasons), "low"


def run_pipeline(parsed: list[dict], profile_path, existing_queue: list[dict]):
    """Returns (updated_queue, new_pending_items).

    parsed: settlement dicts. When produced by the routine agent each carries the
    agent's judgment (eligible / eligibility_reason / confidence); the pipeline
    trusts that and just dedupes + records. Keyword matching is a fallback.
    """
    profile = load_profile(profile_path)
    judgment_by_id: dict[str, dict] = {}
    settlements = []
    for d in parsed:
        s = Settlement.from_dict(d)
        settlements.append(s)
        judgment_by_id[s.id] = d
    settlements = dedupe(settlements)

    existing_ids = {row["id"] for row in existing_queue}
    queue = list(existing_queue)
    new_pending: list[dict] = []

    for s in settlements:
        reason, confidence = _eligibility(s, judgment_by_id.get(s.id, {}), profile)
        if reason is None:
            continue  # not eligible
        row = s.to_dict()
        is_new = s.id not in existing_ids
        row.update({
            "status": "pending_confirm",
            "match_reason": reason,
            "confidence": confidence,
            "discovered_at": _now(),
            "submitted_at": None,
        })
        queue = upsert(queue, row)
        if is_new:
            new_pending.append(next(r for r in queue if r["id"] == s.id))

    return queue, new_pending
