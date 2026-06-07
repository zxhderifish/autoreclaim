---
name: autoreclaim-confirm
description: Use when the user wants to file this week's AutoReclaim settlement claims — opens each pending claim form in the browser, pre-fills it with local PII, checks eligibility honestly, and submits only after the user's explicit OK.
---

# AutoReclaim — confirm & file pending claims

Run from the local autoreclaim **code** repo on the user's Mac, with Claude Desktop's
**Claude in Chrome** browser tools available. Personal data lives in the sibling
`../autoreclaim-data` (the queue + encrypted PII) — NOT in `data/` inside the code repo.

## 1. Load the queue + PII (from the data store)
```bash
export AUTORECLAIM_DATA_DIR="$(cd ../autoreclaim-data && pwd)"
# (Mode 2 / cloud data repo only) pull latest first:
# git -C ../autoreclaim-data pull
# pending items:
.venv/bin/python -c "from autoreclaim.queue import load_queue; from autoreclaim.config import data_dir; import json; print(json.dumps([r for r in load_queue(data_dir()/'queue.jsonl') if r['status']=='pending_confirm']))"
# decrypted PII (key from Keychain):
.venv/bin/python -c "from autoreclaim.pii import load_pii; from autoreclaim.config import data_dir; import json; print(json.dumps(load_pii(data_dir()/'pii.enc')))"
```
**Sanity-check the PII once:** if fields look like placeholders (empty, "test",
"111-111-1111"), tell the user ONE time to re-run `onboarding/setup_pii.py` with real
values and reload — do NOT nag on every form.

## 2. Browser tools
Use **Claude in Chrome** (`navigate`, `get_page_text`, `read_page`, `find`, `form_input`).
Load them once up front. To find the real claim-form link, use `find` / `read_page` — do
NOT use `javascript_tool` to read hrefs (the admin sites often block it).

## 3. For EACH pending item
   a. **Eligibility first (honesty gate).** Read the settlement's eligibility conditions.
      If qualifying depends on something only the user knows (received a breach notice,
      bought X in a date range, a Class Member ID, a VIN, proof docs), ASK the user before
      filing. If they don't qualify, or it needs an ID / proof you can't supply, mark it
      `needs_human` with a short note (where to get the ID, the deadline, what they can
      claim) and move on:
      `.venv/bin/python -m autoreclaim.mark_status <id> needs_human`
   b. **Open + pre-fill.** `navigate` to `claim_url`; if it's a landing page, `find` the
      "Submit Claim" link and navigate to the actual form. Read the form and `form_input`
      each field from PII (name, address, email, phone, payout preference). Answer
      eligibility questions honestly from what the user told you.
   c. **STOP before submit.** Show a table of what you filled + the attestation text, and
      wait for the user's explicit "submit <name>". Never click submit without it.
   d. On their OK, click submit, then:
      `.venv/bin/python -m autoreclaim.mark_status <id> submitted`

## 4. Finish
Give a status overview (filed / ready-to-submit / needs_human — with why + deadlines).
Then persist the queue:
```bash
git -C ../autoreclaim-data add queue.jsonl && git -C ../autoreclaim-data commit -m "chore: filed claims"
# Mode 2 (cloud data repo) only: git -C ../autoreclaim-data push
```

Never submit a claim the user hasn't explicitly confirmed. Never invent eligibility.
Never put PII anywhere but the local `pii.enc`.
