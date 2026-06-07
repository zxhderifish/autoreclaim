---
name: autoreclaim-onboard
description: Use to set up AutoReclaim end-to-end after cloning the code repo — collects the category profile by chat, sets up a separate data store, guides local encrypted PII, picks a run mode (local-only OR cloud-discovery+local-filing), and creates the schedule via the scheduled-task tool. The model never sees PII values.
---

# AutoReclaim onboarding

Run from the cloned AutoReclaim **code** repo on the user's Mac. Goal: take a fresh
clone to a working, scheduled setup. Personal data goes in a SEPARATE data store so the
code repo stays shareable; PII stays local and must NOT pass through this conversation.

**For discrete choices (run mode) use the `AskUserQuestion` tool** (interactive,
highlighted options). For the brand profile (Step 2) just show a grouped markdown list
and let the user reply in plain text — don't force brands through AskUserQuestion.
Minimize typing either way.

## Step 1 — Environment
```bash
[ -d .venv ] || (python3 -m venv .venv && .venv/bin/pip install -e .)
```

## Step 2 — Category profile (auto-fill, ask almost nothing)
The default pack exists so the user does NOT have to think — so **don't dump the full list
on them**. Brand names aren't PII. Keep this to ~2 short messages, no big tables.

**(a) One sentence, NO list.** Tell the user you've auto-added the brands almost everyone
uses (~50 across big tech, payments, streaming, retail, rides/food, credit bureaus,
gaming, fintech) so they don't have to pick — *"just say if there's any you want removed."*
Add the whole internal pack (below) to the profile. Show the full list **only if they ask**.

**(b) Person-specific picks — use `AskUserQuestion`** (multiSelect, so they tap instead of
type), **one question per category**: bank/cards, phone carrier, internet/TV, insurance,
car, airline. Use the first 4 options from each row of the INTERNAL hints below as the
choices (Other covers the rest). AskUserQuestion allows up to 4 questions per call, so
batch them (e.g. 4 then 2). Skip a category that clearly doesn't apply.

Merge: internal pack − their removals + their bank/carrier/ISP/insurance/car/airline picks
+ any extras → answers object (keys `retail`, `banks`, `subscriptions`, `isp_carrier`,
`tech_social`, `offline_services`). **Hold the answers** until Step 4.

> **INTERNAL default pack** — add all of these to the profile; display only if the user asks:
> tech/accounts: amazon, google, apple, microsoft, meta/facebook, instagram, youtube, linkedin, x/twitter, tiktok, reddit, snapchat · payments: paypal, venmo, cash app, zelle, apple pay, google pay · streaming: netflix, spotify, disney+, hulu, max/hbo, prime video, paramount+, peacock, apple tv+, youtube premium · retail/pharmacy: walmart, target, costco, best buy, ebay, home depot, lowe's, cvs, walgreens, kroger, nike · rides/food: uber, lyft, doordash, grubhub, instacart, starbucks, mcdonald's, chipotle · credit bureaus: equifax, experian, transunion · tickets/travel: ticketmaster, expedia, airbnb, marriott, hilton · gaming/devices: playstation, xbox, nintendo, steam, samsung, dell, hp · fintech/crypto: robinhood, coinbase, sofi, chime, affirm, klarna
>
> **INTERNAL person-specific option hints** — show a row only if the user asks "what are my options":
> bank: Chase, Bank of America, Wells Fargo, Capital One, Amex, Citi, Discover, US Bank · carrier: Verizon, AT&T, T-Mobile, Mint, Boost · internet/TV: Xfinity/Comcast, Spectrum, Cox, AT&T, Verizon Fios · airline: Delta, United, American, Southwest, JetBlue · insurance: Geico, Progressive, State Farm, Allstate, Aetna, UnitedHealthcare, Cigna, Blue Cross · car: Toyota, Honda, Ford, Chevrolet, Tesla, Hyundai, Nissan, Subaru

## Step 2b — Gmail gap-fill (optional, default pack stays primary)
After the base profile (pack + picks) is assembled, offer to gap-fill from Gmail. Use
`AskUserQuestion`: **"Want me to scan your Gmail to catch anything we missed? I only look
at WHO emailed you (sender domains) — never the contents."**

- **No** → skip; use the base profile.
- **Yes** →
  1. **Check whether a Gmail tool is actually callable right now** — look for an email MCP
     tool (a `search_threads` / `list_threads`-style tool). Do NOT rely on a connector-
     registry list — it can read empty even when connected. If no Gmail/email tool is
     callable, tell the user **once** and move on (do NOT loop asking): *"To gap-fill from
     Gmail, connect it in Settings → Connectors (read-only). Heads up — the tool usually
     only shows up after you restart Claude / open a new session, so I'll finish onboarding
     now with your base profile. After restarting, just say 'do the Gmail gap-fill' and I'll
     run it."* Then **skip to Step 3**. If a Gmail tool IS callable, continue.
  2. Use the Gmail connector to list the **sender addresses/domains** of emails from the
     **last 24 months** (deduped). Do NOT read bodies, subjects, or recipients.
  3. Extract brand keywords and diff against the base profile:
     ```bash
     echo '<senders-json-array>' | .venv/bin/python -c "import sys,json; from autoreclaim.gmail_brands import sender_domains_to_keywords, new_brands; from autoreclaim.match import load_profile; from autoreclaim.config import data_dir; senders=json.load(sys.stdin); found=sender_domains_to_keywords(senders); existing=load_profile(data_dir()/'profile.json')['keywords'] if (data_dir()/'profile.json').exists() else []; print(json.dumps(new_brands(found, existing)))"
     ```
     (Before profile.json exists, pass the in-memory base answers' keywords as `existing`.)
  4. Show the new finds: **"Found these in your inbox that aren't in your profile yet:
     [...] — which should I add?"** Let the user reply in plain text.
  5. Merge the confirmed new brands into the answers object.

If anything fails (connector unavailable, scan error), skip silently and use the base
profile. The whole onboarding works without Gmail.

## Step 3 — Pick a run mode
Use the **`AskUserQuestion`** tool to ask which mode (don't make them type):
- **Mode 1 — Local-only:** discovery + matching + filing all run on their Mac via a
  local Desktop scheduled task. Nothing goes to the cloud. Most private; needs the Mac
  on / app running (a missed run is caught up on wake).
- **Mode 2 — Cloud discovery + local filing:** a cloud routine discovers + emails
  weekly (runs even with the Mac off); a local Desktop task does the filing with local
  PII. Email + profile live in a private data repo.

## Step 4 — Data store (separate from code → code stays shareable)
Data lives OUTSIDE the code repo. `config.data_dir()` auto-resolves to the sibling
`../autoreclaim-data`, so no env var is needed when it's a sibling.

- **Mode 1 (local-only):** local sibling, git-init, do NOT push:
```bash
mkdir -p ../autoreclaim-data && git -C ../autoreclaim-data init -q && printf 'pii.enc\n' > ../autoreclaim-data/.gitignore
```
- **Mode 2 (cloud):** PRIVATE GitHub data repo cloned as the sibling:
```bash
gh repo create autoreclaim-data --private --clone ../autoreclaim-data
grep -qxF 'pii.enc' ../autoreclaim-data/.gitignore 2>/dev/null || echo 'pii.enc' >> ../autoreclaim-data/.gitignore
```
(`pii.enc` is gitignored even in the private repo — PII must never be pushed, because
the cloud routine clones this repo.)

Then write the profile — keep the user's **deliberate picks** separate from the broad
**default pack** so matching can weight them differently. Write `profile.json` with TWO keys:
- `keywords`: the user's deliberate picks (bank / carrier / ISP / insurance / car / airline
  + any brand they explicitly added or kept)
- `common_pack`: the broad default pack you auto-added (everyone-has-these)
- `email`: the user's email — powers the **free data-breach scan** (XposedOrNot) and Gmail gap-fill. Ask for it (they've agreed email can be used for these).

```bash
mkdir -p ../autoreclaim-data && cat > ../autoreclaim-data/profile.json <<'JSON'
{
  "email": "you@example.com",
  "keywords": ["amex", "chase", "bank of america", "verizon", "xfinity", "toyota", "geico"],
  "common_pack": ["amazon", "google", "apple", "netflix", "spotify", "paypal", "uber", "equifax", "experian", "transunion"]
}
JSON
```
Replace with the real values (all lowercase). **Write this two-key JSON directly — don't
run `build_profile.py`, which would flatten the split.** Confirm the file exists.

## Step 5 — PII (LOCAL ONLY — do NOT collect these values yourself)
Full name / address / phone must NEVER pass through this conversation or the model.
Tell the user to run, in their own terminal:
```bash
.venv/bin/python onboarding/setup_pii.py
```
and enter details there. Confirm only that `../autoreclaim-data/pii.enc` now exists
(gitignored) — without reading it.

## Step 6 — Create the schedule (scheduled-task MCP tool)
Make a LOCAL weekly task with `create_scheduled_task`. The prompt must be
self-contained and hardcode the ABSOLUTE code-repo path (find it with `pwd`).

- **Mode 1 — task `autoreclaim-weekly`** (cron `0 9 * * 1` = Mondays 9am local). A FRESH
  session with no memory runs this prompt, so make it self-contained AND point it at
  CLAUDE.md (one source of truth — don't duplicate the schema/method):
  > cd <abs-repo>; ensure `.venv` (create it + `.venv/bin/pip install -e .` if missing);
  > make sure `AUTORECLAIM_DATA_DIR` points at the `../autoreclaim-data` checkout. **Read
  > this repo's CLAUDE.md and follow its discovery flow EXACTLY** — its settlement schema,
  > the "site-by-site, one pass, don't grep-thrash" extraction method, and the `common_pack`
  > (conservative / low-confidence) vs `keywords` (deliberate) handling. This task is
  > **LOCAL-ONLY (Mode 1)**: instead of emailing, post a **desktop notification** summarizing
  > the new pending. After `run_discovery`, for each new pending open its claim_url and
  > **PRE-FILL** with local PII from `../autoreclaim-data/pii.enc`, **STOP before submit**,
  > and leave it for the user to confirm. Commit `queue.jsonl` in ../autoreclaim-data (local,
  > no push). Never submit without explicit user confirmation; never invent eligibility;
  > never put PII anywhere but the local pii.enc.

- **Mode 2 — task `autoreclaim-file`** (cron `0 18 * * *` = daily 6pm). Prompt:
  > cd <abs-repo>; `git -C ../autoreclaim-data pull`; read pending from
  > ../autoreclaim-data/queue.jsonl; for each, open claim_url + PRE-FILL with local PII,
  > **STOP before submit** for the user to confirm; on confirm run
  > `.venv/bin/python -m autoreclaim.mark_status <id> submitted`; push queue.jsonl. Never
  > submit without confirmation; never invent eligibility; PII stays in local pii.enc only.

  Then guide the user through the one-time CLOUD routine setup via `routine/SETUP.md`:
  build the routine with `/schedule` (prompt = `routine/prompt.md`, both repos, weekly,
  email connector); the only remaining WEB steps are the environment network allowlist,
  the email connector, and the data-repo branch-push permission.

## Step 7 — First run (discover now)
As the last step, **immediately run one real discovery pass** so the user sees real results
right away — don't call it a "smoke test", just run it. Do it the SAME way the weekly task
will: read CLAUDE.md and follow its discovery flow (fetch → extract per its schema/method →
`run_discovery`), then the Mode 1 desktop notification + pre-fill. Show the user the
resulting queue (settlement · est. payout to them · deadline · proof? · confidence · claim
link). This writes a real `queue.jsonl` — not a simulation. (To re-run anytime: Routines →
`autoreclaim-weekly` → Run now.)

## Finish
Commit the profile (Mode 2 also push). Never add pii.enc.
```bash
git -C ../autoreclaim-data add profile.json && git -C ../autoreclaim-data commit -m "chore: onboarding profile"
# Mode 2 only: git -C ../autoreclaim-data push
```
