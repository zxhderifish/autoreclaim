from __future__ import annotations

import os
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parent.parent


def data_dir() -> Path:
    """Where profile.json / queue.jsonl / pii.enc live.

    The code repo (this one) is meant to be public and contains NO personal data.
    All data lives in the separate private `autoreclaim-data` repo. Resolution order:

    1. $AUTORECLAIM_DATA_DIR  (explicit — used by the cloud Routine, which clones
       autoreclaim-data alongside the code repo)
    2. ../autoreclaim-data    (sibling clone next to the code repo)
    3. ./data                 (in-repo dev fallback; gitignored, never committed)
    """
    env = os.environ.get("AUTORECLAIM_DATA_DIR")
    if env:
        return Path(env)
    sibling = _REPO_ROOT.parent / "autoreclaim-data"
    if sibling.exists():
        return sibling
    return _REPO_ROOT / "data"
