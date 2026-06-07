from __future__ import annotations

from pathlib import Path

from autoreclaim import pii

FIELDS = ["full_name", "address_line1", "address_line2", "city", "state",
          "zip", "email", "phone", "payout_preference"]

# Fields claim forms genuinely need (address_line2 / payout_preference are optional).
_REQUIRED = ["full_name", "address_line1", "city", "state", "zip", "email", "phone"]
_PLACEHOLDERS = {"test", "asdf", "qwerty", "n/a", "na", "xxx", "none", "abc"}


def _is_placeholder(value: str) -> bool:
    s = (value or "").strip().lower()
    if not s:
        return True
    if s in _PLACEHOLDERS or s.startswith("test"):
        return True
    digits = s.replace("-", "").replace(" ", "").replace("(", "").replace(")", "")
    if digits and set(digits) <= {"1"}:  # e.g. 111-111-1111
        return True
    return False


def validate_pii(data: dict) -> list[str]:
    """Return REQUIRED fields that are empty or look like placeholders."""
    return [f for f in _REQUIRED if _is_placeholder(data.get(f, ""))]


def main() -> None:
    data = {}
    print("AutoReclaim PII setup — stored encrypted locally, key in Keychain. Nothing uploaded.")
    for field in FIELDS:
        data[field] = input(f"{field.replace('_', ' ')}: ").strip()

    bad = validate_pii(data)
    if bad:
        print(f"\n⚠️  These required fields look empty or like placeholders: {', '.join(bad)}")
        print("Claim forms need your REAL values to auto-fill — otherwise you'll fix each form by hand.")
        if input("Save anyway? (y/N): ").strip().lower() != "y":
            print("Not saved. Re-run onboarding/setup_pii.py when you have real values.")
            return

    from autoreclaim.config import data_dir
    out = data_dir() / "pii.enc"
    pii.save_pii(out, data)
    assert pii.load_pii(out) == data
    print(f"Encrypted PII written to {out} (gitignored). Decryption verified.")


if __name__ == "__main__":
    main()
