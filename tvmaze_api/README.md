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
TODO (author).

## Limitations and assistance
- Only show-level data is stored. Episode counts are fetched live; cast and schedules are not used.
- There are no user accounts: everyone using the same Supabase project shares one list.
- Streamlit reruns the script on every click, so the app reloads the saved list each time. That's fine for a personal list of a few hundred shows.
- Tested end to end on 2026-11-25: live API fetch, `--test`, `--file shows_sample.json` (5 rows) and `--top 5` against Supabase. App tested in the browser (search, save, filter, detail view with episode count, remove) and in demo mode without Supabase.
- TODO (author): list AI tools used. This project was scaffolded with Claude Code, following the structure of the Books project.
