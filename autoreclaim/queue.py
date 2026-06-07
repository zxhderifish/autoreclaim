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
    """Add new_item, or refresh an existing row by id while PRESERVING its status."""
    out = [dict(i) for i in items]
    for row in out:
        if row["id"] == new_item["id"]:
            preserved_status = row.get("status")
            row.update(new_item)
            if preserved_status is not None:
                row["status"] = preserved_status
            return out
    out.append(dict(new_item))
    return out
