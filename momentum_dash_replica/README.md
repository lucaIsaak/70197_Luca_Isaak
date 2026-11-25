# Momentum Dash replica: Reef

## Purpose
Reef is a Chrome extension (Manifest V3) that replaces the new tab page with a Momentum-style dashboard (background scene, clock, greeting, quote, to-do list) and adds a focus timer. During a focus session, sites on your blocklist are blocked and a coral grows; giving up early bleaches it. Finished corals collect in a personal reef. A second part, "Shadow", shows what websites collect about you and what could be inferred from it. See `PM-doc.md` for the full feature spec (features and acceptance criteria).

## Data collection
All data comes from the user's own browser: what they type (blocklist, to-dos, chosen background image) and, only after the user presses "Start recording", browsing metadata observed by the extension (site names, third-party requests, cookie names, fingerprinting calls). No external API is called. Details: `PRIVACY.md`.

## Data persistence
Everything is stored locally in `chrome.storage` inside the browser. Nothing is sent to a server. This keeps the extension private and means no account or backend is needed.

## User interaction
Open a new tab to see the dashboard. Pick a duration and press "Start focus"; add sites to block, add to-dos, change the background. The toolbar popup shows the timer and blocklist. The "Shadow" page (insights) shows your footprint and digital twin.

## Setup
1. Open `chrome://extensions` and switch on Developer mode.
2. Click "Load unpacked" and select this `momentum_dash_replica` folder.
3. Open a new tab.

No dependencies to install. Requires Chrome 111+. `vendor/three.module.min.js` (three.js r160, MIT, see `vendor/LICENSE-three.txt`) is bundled for the 3D twin view.

### Why the extension asks for these permissions
| Permission | Used for |
|---|---|
| `storage`, `alarms`, `notifications` | Saving settings/to-dos locally, the focus timer, end-of-session notice |
| `declarativeNetRequest` | Blocking distracting sites during focus, and the optional tracker blocking |
| `webRequest`, `<all_urls>` host access | Observing which third parties a site contacts (Shadow), only after recording is started |
| `cookies`, `browsingData` | Showing cookie names/lifetimes and the optional "clean up" action |
| Gmail content script | Detecting the "Message sent" toast to tick off "Send email" to-dos (no email content is read) |

## Screenshot
TODO: add `screenshot.png` of the new tab page.

## Learning
**Writing a spec before building.** I started with a product document (`PM-doc.md`) that lists every feature with acceptance criteria, for example "Sites cannot be removed from the list while a focus session is running". Building against that list made it clear when a feature was done, and it made working with an AI assistant much more predictable: I could point at a criterion instead of describing what I wanted each time. The project then grew in versions (V1 focus tools, V2 "Shadow", up to V2.5 "Protect") and the document grew with it, so it also became the history of my decisions.

**How Chrome extensions are put together (Manifest V3).** I learned that an extension is several separate parts that only talk through messages: a background service worker that can be shut down at any time, pages (new tab, popup, insights), and content scripts that run inside websites. Because the service worker doesn't stay alive, the focus timer stores the session's *end time* and uses `chrome.alarms`, instead of counting down in memory. I also learned the difference between the "isolated" and the "MAIN" world for content scripts: `page-hooks.js` has to run in the page's own world to see which browser features scripts read for fingerprinting, and `page-bridge.js` passes the results on to the extension.

**Challenge: blocking rules deleting each other.** Focus mode, tracker blocking and the protection settings all use `declarativeNetRequest` rules. Each feature adds and removes its own rules, so a feature clearing "its" rules could also remove another feature's rules, for example ending a focus session could remove the blocked trackers. I prevented this by giving each feature its own range of rule IDs (focus mode below 10000, trackers 10000–19999, protections from 20000) so that each part only rewrites its own range. This is written down in `PM-doc.md` under "Technical notes".

**Privacy by design.** Because Shadow observes browsing, I decided early that everything stays in `chrome.storage.local`, recording is off until the user presses "Start recording", and cookie values, form entries and email contents are never stored (see `PRIVACY.md`). Writing the privacy policy forced me to check what the code really collects.

## Limitations and assistance
**Limitations**
- The "Network" page is a demo with about 1,000 simulated avatars. There is no real network or server.
- Gmail detection depends on Gmail's "Message sent" message, so it can break if Gmail changes its page.
- The digital twin's guesses are simple rules meant to illustrate what could be inferred. They are often wrong.
- Chrome only (Manifest V3, Chrome 111+). Data is not synced between devices.
- The acceptance criteria in `PM-doc.md` were used as a manual checklist; there are no automated tests.

**Assistance**
- The code was written with **Claude Code** (Anthropic's AI coding assistant), working from my feature spec in `PM-doc.md`. I defined the features, tested each version in Chrome and decided what to keep or change.
- Claude Code also helped prepare this folder for submission: README, permission table, project `.gitignore`, the contact line in the privacy policy, and the audit in `AUDIT.md`.
- The Learning sections in this README were drafted with Claude Code from the full context of our working session and my project history, which my professor allowed. I reviewed them.
- External code: three.js r160 (MIT license, `vendor/`) for the 3D twin view. No other tutorials or external code.
