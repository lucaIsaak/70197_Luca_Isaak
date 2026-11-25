# Requirements check

Source: `individual-submission.pdf` (Submission Guidelines, 3 pages). Checked on 2026-11-25, branch `submission-structure`.

## Requirements and status

| # | Requirement (from PDF) | Status | Notes |
|---|---|---|---|
| 1 | One **public** GitHub repo with all three projects | partial | Local repo is ready; nothing pushed (not allowed in this run). The repo has to be created/pushed and set to public. |
| 2 | Repo opens when logged out of GitHub | missing | Check after pushing. |
| 3 | Submit repo URL + separate **audit evidence PDF** by email by **Dec 19th** | missing | Your step. |
| 4 | One folder per project | done | `momentum_dash_replica/`, `books_to_scrape/`, `tvmaze_api/` |
| 5 | Root `README.md` linking to all three | done | |
| 6 | Project 1: Momentum Dash replica (browser extension) | done | Copied from `chrome_extension/` ("Reef"). Manifest valid, JS syntax checks pass. Not loaded in Chrome during this run. |
| 7 | Project 2: Books to Scrape: collect data | done | Scraper test run (2 books) OK. |
| 8 | Project 2: store in a database | partial | Code exists (Supabase), but the Supabase host in your `.env` does not resolve (project likely paused or deleted), so write/read was not verified. |
| 9 | Project 2: present through an interface of your choice | **missing** | Only CLI scripts that load data; there is no viewing interface. See open questions. |
| 10 | Project 3: TVmaze API solution that connects to and uses the API | done | `tvmaze.py` tested live (search + index). Supabase loader + `--top` listing written but not verified (same DB issue; `shows` table must also be created from `schema.sql`). |
| 11 | README per project: Purpose | done | All three. |
| 12 | README: Data collection | done | All three. |
| 13 | README: Data persistence | done | All three. |
| 14 | README: User interaction | done / partial | Books: interface TODO (see #9). |
| 15 | README: Setup (install, deps, config, run) | done | `requirements.txt` + `.env.example` added for both Python projects. |
| 16 | README: Learning (what you learned, a challenge, how you approached it) | **missing** | Left as `TODO (author)`: this must be your own reflection (graded 10%). |
| 17 | README: Limitations and assistance (AI tools, tutorials, external code) | partial | TVmaze notes Claude Code use and gaps; others are TODO. |
| 18 | Screenshot or short demonstration per project | partial | TVmaze README has example terminal output; no image screenshots yet. |
| 19 | "Not applicable" + reason for topics that don't apply | n/a so far | e.g. Reef's "Data collection" is filled in rather than N/A. |
| 20 | Run the audit prompt per project, fix, repeat | missing | Must be run by you with your assistant (grading looks at your process). |
| 21 | Sanitized `AUDIT.md` in each project | partial | Skeleton files with the required headings exist; contents TODO. |
| 22 | No secrets / private info in repo; placeholder config | done (pre-check) | `.env` not copied, `.env` git-ignored everywhere, `.env.example` uses placeholders, `.claude/settings.local.json` not copied. A regex scan for keys/Supabase URLs in the new folders found nothing. Not a substitute for the audit. |
| 23 | Appropriate exclusions (`.gitignore`) | done | Root + per-project `.gitignore` (env, caches, venv, generated JSON). |
| 24 | Git usage visible (process) | partial | One local commit on `submission-structure`. Graders look at Git history, so commit your own follow-up work in small steps. |

## What I did
- Created branch `submission-structure` and the three project folders.
- Copied `chrome_extension/` → `momentum_dash_replica/` and `bookscrape_supabase/` → `books_to_scrape/` with `rsync`, excluding nested `.git`, `.claude/`, `.env`, `__pycache__`, `.DS_Store`. Originals untouched.
- Path fix: `load_to_supabase.py` now reads `.env` from the script's folder instead of the current working directory. The extension uses only relative paths, so nothing needed changing.
- Built `tvmaze_api/` in the same style as the book scraper (requests, argparse, JSON output, Supabase loader with `--test`/`--file`, `schema.sql`, RLS read-only policy). Added `--top N` as a simple way to look at stored data. Rate limiting: 0.5 s between calls (TVmaze allows ~20 calls / 10 s) and backoff on HTTP 429.
- Wrote root README, three project READMEs, AUDIT skeletons, root and per-project `.gitignore`, `requirements.txt`.

## Test runs
- `books_to_scrape/scraper.py --limit 2` → OK (2 books).
- `tvmaze_api/tvmaze.py --search office --limit 5` and `--limit 3` (index) → OK. Output kept as `tvmaze_api/shows_sample.json`.
- `load_to_supabase.py --test` (both projects, using the credentials in `bookscrape_supabase/.env`) → **failed**: `httpx.ConnectError: nodename nor servname provided`. The Supabase hostname does not resolve; internet otherwise works. No data was written anywhere.

## Assumptions
1. "Movie part" = project 3, **TVmaze API** (the PDF mentions no movie project; TVmaze is TV shows).
2. The `[path]` placeholders in your instructions meant the `chrome_extension/` and `bookscrape_supabase/` folders already in this repo.
3. The PDF does not prescribe folder names, so I chose `momentum_dash_replica`, `books_to_scrape`, `tvmaze_api`.
4. The "Reef" extension is your Momentum Dash replica (new tab dashboard + focus features).
5. The original folders stay in place but are git-ignored in the root `.gitignore`, so their nested `.git` and real `.env` can't be committed by accident.
6. `books.json` (10 records) and `shows_sample.json` are kept as small sample data; `books100.json` and other `shows*.json` are treated as generated output and git-ignored.
7. TVmaze uses Supabase like the book project ("follow the bookscraper's stack"), with JSON files as the always-available output.
8. Learning, AI-assistance and audit sections were left as TODOs on purpose: they must reflect your own work and process.

## Open questions for you
1. **Supabase:** is the project paused or deleted? Restore it (or create a new one), update `.env` in both project folders, run `schema.sql` (books + shows), then `python load_to_supabase.py --test`.
2. **Books interface (#9):** which interface do you want? Simple options: a Streamlit page reading the `books` table, a small static HTML page using the anon key (read-only RLS is already set up), or a CLI query command like TVmaze's `--top`. I didn't build one because it was outside the scope you gave me.
3. Do you want the original two GitHub repos (`lucaIsaak/chrome_extension`, `lucaIsaak/bookscrape_supabase`) linked from the root README too, to show their earlier commit history?
4. Are the folder names fine, or does your course prefer something like `01_…`, `02_…`?
5. `momentum_dash_replica/PM-doc.md` and `PRIVACY.md` were copied as-is. Please check that they contain nothing private before the repo goes public.
