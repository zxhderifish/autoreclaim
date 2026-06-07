from __future__ import annotations

import json
import sys
from pathlib import Path

from .models import make_id
from .queue import load_queue, save_queue
from .pipeline import run_pipeline
from .notify import render_email
from .config import data_dir


def discover(settlements_path, profile_path=None, queue_path=None) -> str:
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
    return render_email(new_pending)


def main() -> None:
    settlements_path = sys.argv[1] if len(sys.argv) > 1 else "settlements.json"
    email = discover(settlements_path)
    print(email)


if __name__ == "__main__":
    main()
