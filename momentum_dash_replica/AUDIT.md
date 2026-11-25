# Audit: momentum_dash_replica (Reef)

## How the audit was run
The audit prompt from the submission guidelines was run with Claude Code (coding assistant) from this folder on 2026-11-25, read-only: no files modified, no project code executed, nothing committed or pushed. Findings were reviewed, fixes applied, and the audit was run again the same day (run 2). After the README sections were completed, a third run checked the whole repository, including its full Git history (run 3).

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
| 1 | `README.md` | Screenshot, Learning and Limitations/assistance sections missing | Yes |
| 2 | `AUDIT.md` | No audit record | Yes |
| 3 | `PRIVACY.md`, `privacy.html` | Contact placeholder "add your contact ... before publishing" | Yes |

**Possible concerns**
| # | Location | Concern | Action needed? |
|---|---|---|---|
| 4 | `manifest.json` | Broad permissions (`<all_urls>`, cookies, browsingData, webRequest, Gmail content script) not explained in README | Yes: explain, permissions are needed for the features |
| 5 | `vendor/three.module.min.js` | Third-party code; version not documented | Yes: document (license file already included) |
| 6 | folder | No project-level `.gitignore` (relied on root) | Recommended |

No secrets, credentials, emails or local paths were found. No `.env` or `.claude` files in Git history.

## Fixes made
- 3: replaced the placeholder with "open an issue on the GitHub repository" (public profile link, no private email).
- 4: added a permissions table to the README explaining why each permission is needed.
- 5: README now names three.js r160 (MIT).
- 6: added `.gitignore` (`.DS_Store`, `.claude/`, packaged `*.zip`/`*.crx`, signing keys `*.pem`).
- 2: this file.

## Run 2: re-audit
No secrets, credentials or personal data found; ignore rules correct; manifest is valid JSON. Remaining items: issue 1 (author's own sections and screenshot).

## Run 3: whole-repository re-audit
Checked the full Git history of the submission repository (not only the current files) for keys, tokens, Supabase project URLs, emails, local paths and IP addresses, and for sensitive files ever committed (`.env`, `.claude/`, `.DS_Store`, caches). Nothing was found. `.env`, caches and generated output are ignored and only exist locally.

- Issue 1: Learning and Limitations/assistance sections are now written. **Still open:** screenshot.
- No new issues.

## Remaining limitations
- The extension was not loaded in Chrome during the audit (the prompt forbids executing project code).
- Pattern searches cannot prove the absence of sensitive data.
