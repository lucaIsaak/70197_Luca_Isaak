# Audit: tvmaze_api

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
| 1 | `README.md`, `shows_sample.json` | TVmaze data is CC BY-SA licensed; no attribution while a data sample is republished | Yes |
| 2 | `README.md` | Screenshot, Learning and AI-assistance sections missing | Yes |
| 3 | `AUDIT.md` | No audit record | Yes |
| 4 | `README.md` | Referred to a working note outside the project instead of stating the limitation | Yes |

**Possible concerns**
| # | Location | Concern | Action needed? |
|---|---|---|---|
| 5 | `schema.sql` | `create policy` fails when the script is re-run | Yes |
| 6 | `load_to_supabase.py` | `--test` dummy row (id -1) left behind if read-back fails | Yes: small fix |

No API key is needed for TVmaze. No secrets, credentials or personal data found; `.env` is git-ignored and `.env.example` has placeholders only.

## Fixes made
- 1: README section "Data source and license" with TVmaze attribution and CC BY-SA 4.0 link.
- 4: limitation stated directly in the README.
- 5: added `drop policy if exists` before `create policy`.
- 6: the test row is deleted in a `finally` block.
- 3: this file.

## Run 2: re-audit
No secrets or personal data; generated `shows*.json` ignored except the committed sample; imports match `requirements.txt`. Remaining item: issue 2.

## Remaining limitations
- The Supabase step could not be verified (database unreachable during the audit).
- Pattern searches cannot prove the absence of sensitive data.
