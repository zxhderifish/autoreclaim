from __future__ import annotations

import sys
from datetime import datetime, timezone

from .queue import load_queue, save_queue
from .config import data_dir


def mark(item_id: str, status: str, note: str | None = None, queue_path=None) -> None:
    queue_path = queue_path or (data_dir() / "queue.jsonl")
    items = load_queue(queue_path)
    for row in items:
        if row["id"] == item_id:
            row["status"] = status
            if note:
                row["status_note"] = note
            if status == "submitted":
                row["submitted_at"] = datetime.now(timezone.utc).isoformat()
            save_queue(queue_path, items)
            return
    raise KeyError(f"no queue item with id {item_id}")


def main() -> None:
    if len(sys.argv) < 3:
        sys.exit("usage: mark_status <id> <status> [note...]")
    note = " ".join(sys.argv[3:]) or None
    mark(sys.argv[1], sys.argv[2], note=note)
    print(f"{sys.argv[1]} -> {sys.argv[2]}" + (f" ({note})" if note else ""))


if __name__ == "__main__":
    main()
