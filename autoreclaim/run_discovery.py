from __future__ import annotations

import json
import sys
from pathlib import Path

from .models import make_id
from .queue import load_queue, save_queue
from .pipeline import run_pipeline
from .notify import render_email, render_deadline_reminders
from .config import data_dir


def discover(settlements_path, profile_path=None, queue_path=None, sites_path=None) -> str:
    base = data_dir()
    profile_path = profile_path or (base / "profile.json")
    queue_path = queue_path or (base / "queue.jsonl")

    parsed = json.loads(Path(settlements_path).read_text())
    for row in parsed:
        if not row.get("id"):
            row["id"] = make_id(row["title"])

    existing = load_queue(queue_path)
    queue, new_pending = run_pipeline(parsed, profile_path=profile_path, existing_queue=existing)
    save_queue(queue_path, queue)
    email = render_email(new_pending)

    # Unactioned items near their deadline: needs_human must not rot silently.
    reminders = render_deadline_reminders(queue, exclude_ids={r["id"] for r in new_pending})
    if reminders:
        email = f"{email}\n\n{reminders}" if email else reminders

    # Source health: a digest that's empty because sources were down is NOT the same
    # as "nothing new" — surface failed sources so partial discovery is visible.
    if sites_path:
        sites = json.loads(Path(sites_path).read_text())
        failed = sorted(domain for domain, text in sites.items() if not text)
        if failed:
            note = (f"Note: {len(failed)} source(s) unreachable this week: "
                    f"{', '.join(failed)} — results may be incomplete.")
            email = f"{email}\n\n{note}" if email else note
    return email


def main() -> None:
    settlements_path = sys.argv[1] if len(sys.argv) > 1 else "settlements.json"
    sites_path = sys.argv[2] if len(sys.argv) > 2 else None
    email = discover(settlements_path, sites_path=sites_path)
    print(email)


if __name__ == "__main__":
    main()
