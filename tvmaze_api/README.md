# TVmaze API

## Purpose
A small app for the public TVmaze API. In a Streamlit web interface (`app.py`) you search TV shows live on TVmaze, save the ones you like to your own list in Supabase, filter and chart that list, and open a detail view that fetches the number of seasons and episodes live from TVmaze. Command-line scripts (`tvmaze.py`, `load_to_supabase.py`) do the same fetching and loading in bulk.

## Data collection
`tvmaze.py` calls https://api.tvmaze.com with `requests`:
- `/search/shows?q=<term>` when `--search` is given,
- `/shows?page=N` (the paged show index) otherwise.

`app.py` uses the same functions for its live search, plus `/shows/<id>/episodes` for the season and episode count in the detail view. API results are cached in the app (10 minutes for searches, 1 hour for episode counts), so repeated searches don't call TVmaze again.

No API key is needed. TVmaze allows about 20 requests per 10 seconds per IP, so the script waits `--delay` seconds (default 0.5) after each call and retries with a growing pause if it receives HTTP 429.

## Data persistence
Results are written to a JSON file (`shows_sample.json` is a small committed example; other `shows*.json` files are git-ignored) and can be upserted into the `shows` table in Supabase (`schema.sql`). The TVmaze show id is the primary key, so re-loading updates rows instead of duplicating them. Same security model as the Books project: public read only, writes with the service-role key from `.env`.

In the app, the `shows` table is your personal list: Save adds a show, Remove deletes it. Only the show data is stored, not search history. Episode counts are always fetched live and not stored, because they change while a show is running.

## User interaction
**Web interface**
```bash
streamlit run app.py
```
Opens at http://localhost:8501.
- **Search:** type a show name. Results come live from TVmaze with poster, year, rating, genres and network. Press **Save** to add a show to your list.
- **My shows:** your saved shows as a table, with sidebar filters (genre, minimum rating, status), summary numbers and a chart of shows per genre. The detail view shows poster, summary, network and years, plus the live season and episode count. **Remove** deletes the show from your list.

Without Supabase (no `.env`, or the project is paused), the app runs as a read-only demo: search still works, the list shows `shows_sample.json`, and Save/Remove are disabled.

**Command line**
```bash
python tvmaze.py --search "office" --limit 5 --out shows.json
python tvmaze.py --limit 20 --out shows.json
python load_to_supabase.py --test
python load_to_supabase.py --file shows.json
python load_to_supabase.py --top 5
```
Example output:
```
[1/5] The Office (2005-03-24) rating=8.5
[2/5] The Office (2001-07-09) rating=7.9
...
Wrote 5 records to shows.json
```

## Data source and license
Show data comes from [TVmaze](https://www.tvmaze.com) via its public API and is licensed under [CC BY-SA 4.0](https://creativecommons.org/licenses/by-sa/4.0/). `shows_sample.json` contains TVmaze data (unchanged apart from removing HTML tags from summaries) and is shared under the same license.

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # needed for saving in the app and for load_to_supabase.py
```
Tested with Python 3.13. Run `schema.sql` in the Supabase SQL Editor (safe to re-run) before `load_to_supabase.py`. `tvmaze.py`, and the app in demo mode, work without any configuration.

## Screenshot
TODO: add a screenshot of the app (Search and My shows).

## Learning
**API instead of scraping.** Compared with the Books project, the TVmaze API returns structured JSON, so there was no HTML to parse. But the data is nested (network → country, rating → average, image → original) and summaries contain HTML tags, so I still needed a step (`parse_show`) that flattens each show into one clean record matching my table. I also learned to respect the API's rate limit (about 20 requests per 10 seconds): the script waits between calls and backs off when it gets HTTP 429, and the app caches results so repeating a search doesn't call TVmaze again.

**What is worth storing.** I store the shows a user saves, but not the episode counts: those change while a show is running, so the app fetches them live when a show is opened. Deciding what to store and what to fetch live was a design question I hadn't thought about before.

**Challenge: a table that wasn't there.** After the Supabase project was restored, the loader kept failing with "Could not find the table 'public.shows'". I checked which tables the API could see, and only `books` was listed. In the end the cause was simple: I had pasted `schema.sql` into the SQL Editor, but the query had never been run. The results panel still said "Click Run to execute your query". When I ran it, Supabase warned about "destructive operations". That came from the `drop policy if exists` line, which only resets the read-only access rule so the script can be run more than once; it doesn't delete any data. I learned to check the result of every step instead of assuming it worked, and to understand what a warning refers to before confirming it.

**Challenge: Streamlit reruns everything.** Streamlit runs the whole script again on every click. My first version used tabs, and every time a filter changed, the page jumped back to the Search tab. The fix was to replace the tabs with a radio switch whose value is stored in the session state, so the app remembers which view is open, and to show the filters only on "My shows". A second bug came from pandas: a missing rating becomes `NaN`, which counts as "true" in Python, so the app showed "nan" instead of "–" until I converted missing values back to `None`.

**A deliberate decision about scope.** I first wanted to add AI features to step into a show's world: generating merch (card decks, shirts, puzzles), videos with me or friends in the series, or a video game. I decided against it. Posters, logos and characters are copyrighted, and putting real people (friends or actors) into AI videos raises consent and likeness problems. It would also have been far more work than the deadline allowed, and graders would have needed paid API keys to try it. I also considered a "swipe to like or dislike" app and an AI text adventure, but they didn't interest me enough. So I chose a simple, useful interface: search, save your own list, and see live episode counts. The assignment says simple solutions can earn full marks, and this one I can fully explain.

## Limitations and assistance
**Limitations**
- Only show-level data is stored. Episode counts are fetched live; cast and schedules are not used.
- There are no user accounts: everyone using the same Supabase project shares one list.
- The app saves and removes shows with the service-role key from `.env`, because writing needs it. It is meant to run locally on your own computer and should not be deployed publicly in this form.
- Streamlit reruns the script on every click, so the app reloads the saved list each time. That's fine for a personal list of a few hundred shows.
- Tested end to end on 2026-11-25: live API fetch, `--test`, `--file shows_sample.json` (5 rows) and `--top 5` against Supabase. App tested in the browser (search, save, filter, detail view with episode count, remove) and in demo mode without Supabase.

**Assistance**
- This project was built with **Claude Code** (Anthropic's AI coding assistant), following the structure of my Books project. I chose the project idea and scope, set up and debugged Supabase, and tested the app.
- Claude Code also helped with the README and the audit in `AUDIT.md`.
- The Learning sections in this README were drafted with Claude Code from the full context of our working session and my project history, which my professor allowed. I reviewed them.
- Data: TVmaze API (CC BY-SA 4.0, see above). Libraries: requests, supabase-py, Streamlit, pandas. No other tutorials or external code.
