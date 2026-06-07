# Architecture

AutoReclaim is a weekly agent loop wrapped around a small, deterministic Python pipeline.
The agent does the fuzzy work (reading settlement pages, judging eligibility, filling forms);
the Python does the work that must be exact and testable (dedupe, scoring, the queue, encryption).

## The three planes

The hardest constraint shapes everything: **sharable code must never touch your PII.**
So the system is split into three planes that live in different places.

```
┌─────────────────────┐     ┌──────────────────────────┐     ┌────────────────────┐
│  CODE (this repo)    │     │  DATA (private repo)     │     │  PII (local only)  │
│  public              │     │  autoreclaim-data        │     │  pii.enc           │
│                      │     │                          │     │                    │
│  agent skills        │     │  profile.json            │     │  name / address /  │
│  fetch + clean       │ ──▶ │  queue.jsonl             │ ──▶ │  phone, encrypted  │
│  match / pipeline    │     │  history                 │     │  (key in keychain) │
│  breach lookup       │     │                          │     │  never pushed      │
└─────────────────────┘     └──────────────────────────┘     └────────────────────┘
```

The code repo is meant to be public. Your profile and the running queue live in a separate
private repo. Your actual personal details are encrypted in `pii.enc`, which is gitignored in
*every* repo and never leaves the machine.

## Discovery flow (weekly)

1. **Fetch + clean** (`fetch.py`, `clean.py`) — pull the major settlement-tracker pages and
   reduce HTML to readable text, preserving claim-form links so they survive into matching.
2. **Match** (the agent + `match.py`) — the agent reads the cleaned pages against your profile
   and judges *semantically* whether you qualify, rather than relying on raw keyword overlap.
   Your deliberate picks (`keywords`) are matched normally; the broad "everyone has these"
   defaults (`common_pack`) are matched conservatively and marked low-confidence.
3. **Breach evidence** (`breach.py`) — for data-breach settlements, a free XposedOrNot lookup
   tells the agent which breaches your email is *actually* in, so those matches are hard
   evidence rather than guesses.
4. **Pipeline** (`pipeline.py`, `dedupe.py`, `queue.py`, `run_discovery.py`) — the matched
   settlements are deduplicated against what you've already seen, written to `queue.jsonl`, and
   a digest email body is produced.
5. **Notify** (`notify.py` / email connector) — you get a digest of what's new.

## Filing flow (local, on confirmation)

Filing always runs locally and always stops short of submitting:

1. Read pending items from the queue.
2. Open each claim form and pre-fill it with decrypted PII (`pii.py`).
3. **Stop before submit.** You review and confirm each claim yourself.
4. Mark confirmed claims as submitted (`mark_status.py`).

## Module map

| Module | Responsibility |
|--------|----------------|
| `fetch.py` / `clean.py` | retrieve and normalize settlement pages |
| `match.py` | load the profile, score candidate settlements |
| `breach.py` | free email-breach lookup (XposedOrNot) |
| `pipeline.py` / `dedupe.py` / `queue.py` | dedupe, persist, and manage the queue |
| `run_discovery.py` | orchestrate one discovery pass + build the digest |
| `pii.py` | encrypt/decrypt local PII (Fernet, key in OS keychain) |
| `notify.py` | digest output |
| `mark_status.py` | update a claim's status after confirmation |
| `gmail_brands.py` | optional: derive brand profile from email sender domains |
| `onboarding/` | guided setup + local PII entry |

## Why an agent, not a parser

Settlement pages are unstructured and change constantly, and eligibility is written in prose
("anyone who purchased Brand X between 2019 and 2022 in California"). A rigid parser would miss
most of it. Using an agent for the judgment step — with the deterministic pipeline handling
everything that must be exact — is the core design bet.
