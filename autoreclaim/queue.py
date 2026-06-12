from __future__ import annotations

import json
from pathlib import Path


def load_queue(path) -> list[dict]:
    p = Path(path)
    if not p.exists():
        return []
    out = []
    for line in p.read_text().splitlines():
        line = line.strip()
        if line:
            out.append(json.loads(line))
    return out


def save_queue(path, items: list[dict]) -> None:
    p = Path(path)
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text("\n".join(json.dumps(i, ensure_ascii=False) for i in items) + "\n")


def upsert(items: list[dict], new_item: dict) -> list[dict]:
    """Add new_item, or refresh an existing row by id while PRESERVING its status
    (and submitted_at — a weekly re-discovery must not reset a filed item)."""
    out = [dict(i) for i in items]
    for row in out:
        if row["id"] == new_item["id"]:
            preserved = {k: row[k] for k in ("status", "submitted_at") if row.get(k) is not None}
            row.update(new_item)
            row.update(preserved)
            return out
    out.append(dict(new_item))
    return out
