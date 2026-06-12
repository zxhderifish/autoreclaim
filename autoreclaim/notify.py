from __future__ import annotations

from datetime import date

# Statuses where the user still has something to do before the deadline.
_ACTIONABLE = {"pending_confirm", "needs_human"}


def render_deadline_reminders(queue: list[dict], exclude_ids=frozenset(),
                              today: date | None = None, window_days: int = 14) -> str:
    """Items the user has NOT acted on whose deadline is within window_days.

    Without this, needs_human items sink silently until their deadline passes."""
    today = today or date.today()
    due: list[tuple[int, dict]] = []
    for row in queue:
        if row.get("status") not in _ACTIONABLE or row.get("id") in exclude_ids:
            continue
        deadline = row.get("deadline")
        if not deadline:
            continue
        try:
            days = (date.fromisoformat(str(deadline)[:10]) - today).days
        except ValueError:
            continue
        if 0 <= days <= window_days:
            due.append((days, row))
    if not due:
        return ""
    due.sort(key=lambda t: t[0])
    lines = [f"Deadlines approaching — {len(due)} item(s) in your queue still need action:", ""]
    for days, row in due:
        when = "due TODAY" if days == 0 else f"{days} day(s) left"
        lines.append(f"- {row.get('title', 'Untitled')} — {when} (by {row.get('deadline')})")
        if row.get("status_note"):
            lines.append(f"  note: {row['status_note']}")
        lines.append(f"  {row.get('claim_url') or '(no link)'}")
        lines.append("")
    return "\n".join(lines).rstrip()


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
