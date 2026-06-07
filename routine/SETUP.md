# Configure the AutoReclaim weekly Routine

This project uses TWO repos:
- `autoreclaim` — code (this repo; meant to become public)
- `autoreclaim-data` — PRIVATE personal data (`profile.json` + `queue.jsonl`)

PII (`pii.enc`) stays local and is in NEITHER repo.

1. Push BOTH repos to GitHub (both private for now):
   - `autoreclaim` (code)
   - `autoreclaim-data` (your profile + queue)
2. Go to https://claude.ai/code/routines → New routine → Remote.
3. Prompt: paste `routine/prompt.md`.
4. Repositories: add BOTH `autoreclaim` and `autoreclaim-data`. For `autoreclaim-data`,
   enable "Allow unrestricted branch pushes" so the routine can commit `queue.jsonl`
   back. Leave `autoreclaim` read-only (default).
5. Environment:
   - Network access → **Custom**. Allowed domains:
     topclassactions.com, claimdepot.com, classaction.org, openclassactions.com,
     consumer-action.org, fileyourclaim.co
     (Keep "include default package managers" checked so pip works.)
   - Environment variable: `AUTORECLAIM_DATA_DIR` = path to the `autoreclaim-data`
     checkout in the cloud workspace (e.g. `../autoreclaim-data`).
6. Connectors: keep only your **email connector** (e.g. Gmail). Remove the rest.
7. Trigger: **Schedule → Weekly**, pick a day/time.
8. Save. Click **Run now** once to smoke-test.
