# AutoReclaim — agent operating instructions

This repo is **public CODE only**. The user's personal data — category profile, queue,
history — lives in a separate PRIVATE repo `autoreclaim-data`. PII (`pii.enc`) is never in
any repo; it stays local on the user's machine.

## Routing — decide this FIRST, before any other action

Work out which job you're doing before you touch anything:

- **Setup / onboarding** — a human asks to "set up" / "install" / "get started", OR
  `../autoreclaim-data/profile.json` does not exist yet → **invoke the `autoreclaim-onboard`
  skill** and follow it. Do NOT start fetching settlements, writing files, or improvising
  setup steps. Onboarding is a guided chat; the skill drives it.
- **File this week's claims** — "file my claims", "process the queue", "review what you
  found" → **invoke the `autoreclaim-confirm` skill**.
- **Scheduled weekly discovery** — you were launched by the `autoreclaim-weekly` task (or
  the cloud Routine) with no human in the loop → follow the **Discovery flow** below.

When a human is interactively asking to get started, it is ALWAYS onboarding — never the
discovery flow. The discovery flow is for the unattended scheduled run.

## Discovery flow (scheduled run)

The weekly task / cloud Routine clones the data repo and sets `AUTORECLAIM_DATA_DIR` to the
`autoreclaim-data` checkout.

1. Set up: `python3 -m venv .venv && .venv/bin/pip install -e .`
   Make sure `AUTORECLAIM_DATA_DIR` points at the `autoreclaim-data` checkout.
2. Fetch raw pages: `.venv/bin/python -c "from autoreclaim.fetch import fetch_all; from autoreclaim.clean import html_to_text; import json,sys; print(json.dumps({k: html_to_text(v) for k,v in fetch_all().items()}))" > sites.json`
3. **You (the agent) read `sites.json` AND the user's profile** (`$AUTORECLAIM_DATA_DIR/profile.json` — it has `keywords` = the user's deliberate picks, and `common_pack` = broad defaults almost everyone has). **Extract efficiently — don't grep-thrash:** sites.json is keyed by domain; go site-by-site in ONE pass — for a small site read it through once, for a large one grep it ONCE for all profile brands to find the relevant blocks and read those; don't re-grep per brand or re-read repeatedly. For EACH open settlement, judge **semantically** whether this user might qualify — use synonyms, product lines, and the eligibility conditions in the description, NOT just keyword overlap; treat `common_pack` brands CONSERVATIVELY (match only if the settlement clearly targets that brand, mark it low confidence), match `keywords` normally. **Data-breach settlements (hard evidence):** run `.venv/bin/python -m autoreclaim.breach` (no args — it reads EVERY email in `profile.json`; the schema supports `emails: [...]` and the legacy single `email`) to get the companies whose breaches the user is ACTUALLY in (free XposedOrNot lookup, no key). Match any open data-breach settlement targeting one of those companies and mark it HIGH confidence — even if the company isn't in keywords/common_pack — and say so in eligibility_reason (e.g. "Your email was in the X breach"). Write ONLY the ones the user might qualify for into `settlements.json`: a JSON list where each item has keys: `source`, `title`, `category_tags` (lowercase words a person would recognize), `deadline` (ISO or null), `claim_url` (the http link to file — links survive in the cleaned text as "text (https://…)", so grab the URL near the settlement; this is the link the user clicks to file manually, so always capture it), `needs_proof` (bool), `attestation_strength` ("normal"/"strict"/"unknown"), `est_payout` (the INDIVIDUAL user's estimated payout — "up to $X" / "$X–$Y" / "pro-rata share"; NOT the total settlement fund. If only a total is stated, note it in eligibility_reason and give the per-person estimate, or null), plus your judgment: `eligible` (true), `eligibility_reason` (one human sentence, e.g. "You bank with Chase"), `confidence` ("high"/"medium"/"low"). Leave `id` out — the pipeline computes it. Be generous on recall (the user confirms before filing); skip only clear non-matches and anything past its deadline.
4. Run the pipeline and write the queue + digest:
   `.venv/bin/python -m autoreclaim.run_discovery settlements.json`
   This reads `profile.json` and writes `queue.jsonl` inside `$AUTORECLAIM_DATA_DIR`, and prints the digest body (empty if nothing new). The digest includes each settlement's `claim_url` so the user can file manually.
5. Notify the user. Cloud Routine → send the digest via the **email connector** (subject: "AutoReclaim weekly digest"). Local Mode-1 task → post a desktop notification. **Whenever you show the user a table of finds, include a "Claim link" column with the `claim_url`** so they can reclaim manually if they want.
6. In the `autoreclaim-data` repo, commit the updated `queue.jsonl` and push.

Never put PII anywhere. The scheduled discovery only discovers/matches/notifies — it does not file claims (filing happens locally via the `autoreclaim-confirm` skill).
