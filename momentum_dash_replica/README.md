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
TODO (author): what you learned, one challenge, and how you approached it.

## Limitations and assistance
TODO (author): incomplete features, and which AI tools / tutorials / external code were used (three.js is bundled under the MIT license).
