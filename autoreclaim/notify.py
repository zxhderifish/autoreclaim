from __future__ import annotations


def render_email(new_pending: list[dict]) -> str:
    if not new_pending:
        return ""
    n = len(new_pending)
    lines = [
        f"AutoReclaim — {n} new settlement(s) you may qualify for",
        "",
    ]
    for i, row in enumerate(new_pending, 1):
        reason = row.get("match_reason") or "profile match"
        conf = row.get("confidence")
        payout = row.get("est_payout") or "amount TBD"
        deadline = row.get("deadline") or "deadline TBD"
        proof = "proof required" if row.get("needs_proof") else "no proof"
        why = f"why: {reason}"
        if conf:
            why += f" (confidence: {conf})"
        lines += [
            f"{i}. {row.get('title', 'Untitled')}",
            f"   {why} | {payout} | by {deadline} | {proof}",
            f"   {row.get('claim_url') or '(no link)'}",
            "",
        ]
    lines += [
        "To file these: open Cowork on your Mac and run  /autoreclaim-confirm",
        "(or Dispatch from your phone: \"process this week's AutoReclaim queue\")",
    ]
    return "\n".join(lines)
