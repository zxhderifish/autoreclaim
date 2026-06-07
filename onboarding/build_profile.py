from __future__ import annotations

import json
from pathlib import Path

QUESTIONS = {
    "retail": "Stores/brands you buy from (comma-separated)",
    "banks": "Banks / credit cards you use",
    "subscriptions": "Subscriptions / apps (Netflix, Spotify, ...)",
    "isp_carrier": "Internet provider / phone carrier",
    "tech_social": "Big tech / social accounts (Meta, Google, ...)",
    "offline_services": "Other services (gym, airline, hospital, ...)",
}


def answers_to_profile(answers: dict) -> dict:
    seen, keywords = set(), []
    for value in answers.values():
        for raw in value.split(","):
            kw = raw.strip().lower()
            if kw and kw not in seen:
                seen.add(kw)
                keywords.append(kw)
    return {"keywords": keywords}


def write_profile(answers: dict) -> Path:
    from autoreclaim.config import data_dir
    profile = answers_to_profile(answers)
    out = data_dir() / "profile.json"
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(profile, indent=2))
    return out


def main() -> None:
    # The onboard skill pipes answers as JSON on stdin, e.g.
    #   echo '{"retail": "amazon, target", "banks": "chase"}' | python onboarding/build_profile.py
    import sys
    answers = json.loads(sys.stdin.read())
    out = write_profile(answers)
    print(f"Wrote {len(answers_to_profile(answers)['keywords'])} keywords to {out}")


if __name__ == "__main__":
    main()
