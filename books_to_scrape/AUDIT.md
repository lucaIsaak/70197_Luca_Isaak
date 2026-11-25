# Audit: books_to_scrape

## How the audit was run
The audit prompt from the submission guidelines was run with Claude Code (coding assistant) from this folder on 2026-11-25, read-only: no files modified, no project code executed, nothing committed or pushed. Findings were reviewed, fixes applied, and the audit was run again the same day.

## What was checked
- Tracked and untracked files (`git ls-files`, `git status`) and files ignored by `.gitignore`
- Pattern search for API keys, tokens, JWTs, Supabase project URLs, emails and local file paths
- Git history of this repo and of the original standalone repo for committed `.env` or `.claude` files
- `.gitignore` coverage (local config, caches, virtual envs, generated output)
- Dependencies vs. imports, setup instructions and configuration examples
- README coverage: purpose, data collection, persistence, user interaction, setup, learning, limitations

## Run 1: findings
**Confirmed issues**
| # | Location | Issue | Action needed? |
|---|---|---|---|
| 1 | `README.md` | Screenshot, Learning and Limitations sections missing | Yes |
| 2 | `AUDIT.md` | No audit record | Yes |

**Possible concerns**
| # | Location | Concern | Action needed? |
|---|---|---|---|
| 3 | `app.py` | Read-only interface used the service-role key (full write access, bypasses RLS) | Yes: least privilege |
| 4 | `schema.sql` | `create policy` fails when the script is re-run | Yes: reproducibility |
| 5 | `books.json` | Contains scraped book descriptions | No: books.toscrape.com is a sandbox built for scraping practice |
| 6 | `README.md` | Python version not stated; app's no-`.env` mode not mentioned | Recommended |

The real `.env` exists only locally and is git-ignored; it was never committed (also checked in the original repo's history). `.env.example` contains placeholders only.

## Fixes made
- 3: `app.py` now prefers the read-only `SUPABASE_ANON_KEY` (added to `.env.example`); the service key is only a local fallback.
- 4: added `drop policy if exists` before `create policy`.
- 6: README states Python 3.13 and explains that the app works without `.env`.
- 2: this file.

## Run 2: re-audit
No secrets, credentials or personal data found; `.env`, `__pycache__` and `books100.json` are ignored; all imports are listed in `requirements.txt`. Remaining item: issue 1.

## Remaining limitations
- The Supabase database could not be reached, so RLS policies and stored data were not inspected.
- Pattern searches cannot prove the absence of sensitive data.
