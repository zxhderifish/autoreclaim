# AutoReclaim — agent operating instructions

This repo holds ONLY code (it is meant to be public). Your personal data — category
profile, queue, history — lives in a separate PRIVATE repo `autoreclaim-data`. PII
(`pii.enc`) is never in any repo; it stays local on the user's machine.

The weekly cloud Routine clones BOTH repos and sets `AUTORECLAIM_DATA_DIR` to the
`autoreclaim-data` checkout. Discovery flow:

1. Set up: `python3 -m venv .venv && .venv/bin/pip install -e .`
   Make sure `AUTORECLAIM_DATA_DIR` points at the `autoreclaim-data` checkout.
2. Fetch raw pages: `.venv/bin/python -c "from autoreclaim.fetch import fetch_all; from autoreclaim.clean import html_to_text; import json,sys; print(json.dumps({k: html_to_text(v) for k,v in fetch_all().items()}))" > sites.json`
3. **You (the agent) read `sites.json` AND the user's profile** (`$AUTORECLAIM_DATA_DIR/profile.json` — it has `keywords` = the user's deliberate picks, and `common_pack` = broad defaults almost everyone has). **Extract efficiently — don't grep-thrash:** sites.json is keyed by domain; go site-by-site in ONE pass — for a small site read it through once, for a large one grep it ONCE for all profile brands to find the relevant blocks and read those; don't re-grep per brand or re-read repeatedly. For EACH open settlement, judge **semantically** whether this user might qualify — use synonyms, product lines, and the eligibility conditions in the description, NOT just keyword overlap; treat `common_pack` brands CONSERVATIVELY (match only if the settlement clearly targets that brand, mark it low confidence), match `keywords` normally. **Data-breach settlements (hard evidence):** if `profile.json` has an `email`, run `.venv/bin/python -m autoreclaim.breach <email>` to get the companies whose breaches this user is ACTUALLY in (free XposedOrNot lookup, no key). Match any open data-breach settlement targeting one of those companies and mark it HIGH confidence — even if the company isn't in keywords/common_pack — and say so in eligibility_reason (e.g. "Your email was in the X breach"). Write ONLY the ones the user might qualify for into `settlements.json`: a JSON list where each item has keys: `source`, `title`, `category_tags` (lowercase words a person would recognize), `deadline` (ISO or null), `claim_url` (the http link to file — links now survive in the cleaned text as "text (https://…)", so grab the URL near the settlement), `needs_proof` (bool), `attestation_strength` ("normal"/"strict"/"unknown"), `est_payout` (the INDIVIDUAL user's estimated payout — "up to $X" / "$X–$Y" / "pro-rata share"; NOT the total settlement fund. If only a total is stated, note it in eligibility_reason and give the per-person estimate, or null), plus your judgment: `eligible` (true), `eligibility_reason` (one human sentence, e.g. "You bank with Chase"), `confidence` ("high"/"medium"/"low"). Leave `id` out — the pipeline computes it. Be generous on recall (the user confirms before filing); skip only clear non-matches and anything past its deadline.
4. Run the pipeline and write the queue + email body:
   `.venv/bin/python -m autoreclaim.run_discovery settlements.json`
   This reads `profile.json` and writes `queue.jsonl` inside `$AUTORECLAIM_DATA_DIR`, and prints the email body (empty if nothing new).
5. If the printed email body is non-empty, send it to the user via the **email connector** (subject: "AutoReclaim weekly digest").
6. In the `autoreclaim-data` repo, commit the updated `queue.jsonl` and push.

Never put PII anywhere. This Routine only discovers/matches/notifies — it does not file claims (filing happens locally via the `/autoreclaim-confirm` skill).
