# Requirements check

Working checklist against the course's submission guidelines (`individual-submission.pdf`, 3 pages). Last checked on 2026-11-25.

## Status

| # | Requirement (from the guidelines) | Status | Notes |
|---|---|---|---|
| 1 | One **public** GitHub repo with all three projects | partial | `lucaIsaak/70197_Luca_Isaak` exists and is public, but nothing has been pushed yet. |
| 2 | Repo opens when logged out of GitHub | partial | The page loads without login; check again after pushing. |
| 3 | Repo URL + separate **audit evidence PDF** by email by **Dec 19th** | open | Not part of the repo. |
| 4 | One folder per project | done | `momentum_dash_replica/`, `books_to_scrape/`, `tvmaze_api/` |
| 5 | Root `README.md` linking to all three | done | |
| 6 | Project 1: Momentum Dash replica (browser extension) | done | "Reef" Chrome extension. Manifest valid, JS syntax checks pass. |
| 7 | Project 2: collect book data | done | `scraper.py` |
| 8 | Project 2: store it in a database | done | Supabase `books` table; `load_to_supabase.py --test` passes. |
| 9 | Project 2: present it through an interface | done | Streamlit app `app.py`, reads the 100 books from Supabase; falls back to local JSON without Supabase. |
| 10 | Project 3: TVmaze API solution that connects to and uses the API | done | Streamlit app `app.py` (live search, save/remove in Supabase, filters, chart, live season/episode count) and CLI (`tvmaze.py`, `load_to_supabase.py`). Verified against Supabase and in demo mode. |
| 11 | README: Purpose | done | All three |
| 12 | README: Data collection | done | All three |
| 13 | README: Data persistence | done | All three |
| 14 | README: User interaction | done | All three |
| 15 | README: Setup (installation, dependencies, configuration, run) | done | `requirements.txt` and `.env.example` in both Python projects |
| 16 | README: Learning (what you learned, a challenge, how you approached it) | done | All three. Drafted with Claude Code from full context (allowed by the professor); to be reviewed by the author. |
| 17 | README: Limitations and assistance (incomplete features, AI tools, tutorials, external code) | done | All three |
| 18 | Screenshot or short demonstration per project | done | Extension: new tab page and Shadow page. Books and TVmaze: home page of each app. |
| 19 | "Not applicable" with a reason for topics that don't apply | done | No topic needed it. |
| 20 | Run the audit prompt per project, review, fix, repeat | done | Run 1 → fixes → run 2 → run 3 (whole repo, full Git history). |
| 21 | Sanitized `AUDIT.md` in each project | done | Findings, decisions, fixes, re-audits, limitations; no secrets. |
| 22 | No secrets or private information; placeholder configuration | done | Confirmed in run 3, including all past commits. |
| 23 | Organized files and appropriate exclusions (`.gitignore`) | done | Root and per-project `.gitignore` |
| 24 | Git usage | partial | Commits on branch `submission-structure`. There is no local `main` yet, while GitHub's default branch is `main`. |

## Before submitting
1. Push the work as `main`, so the repo doesn't open on an empty default branch:
   ```bash
   git branch -m submission-structure main
   git push -u origin main
   ```
2. Open the repo while logged out of GitHub and check that all three folders and READMEs show (#2).
3. Create the audit evidence PDF and send it with the repo link by Dec 19th (#3).
4. Shortly before grading, open the Supabase dashboard so the free project isn't paused.

## Decisions and assumptions
- Project 3 is the TVmaze API project (TV shows). The guidelines don't mention a movie project.
- Folder names are not prescribed by the guidelines; descriptive snake_case names were chosen.
- The two projects that existed before (the extension and the book scraper) were copied into this repo without their own Git history. Their earlier history stays in the separate repos `lucaIsaak/chrome_extension` and `lucaIsaak/bookscrape_supabase`.
- `books.json` (10 books) and `shows_sample.json` (5 shows) are committed as small sample data, so both apps can be tried without Supabase. Larger generated files are git-ignored.
- Both Python projects use the same stack: requests, Supabase, Streamlit.

## Open questions
- Should the two earlier repos be linked from the root README to show the earlier commit history?
- Should this checklist stay in the public repo, or be removed before submitting? It is a working note, not part of the assignment.
