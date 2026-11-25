# TVmaze API

## Purpose
A small command-line client for the public TVmaze API. It searches for TV shows (or reads the show index), cleans each show into a flat record, saves the results as JSON and in a Supabase table, and lists the best-rated stored shows.

## Data collection
`tvmaze.py` calls https://api.tvmaze.com with `requests`:
- `/search/shows?q=<term>` when `--search` is given,
- `/shows?page=N` (the paged show index) otherwise.

No API key is needed. TVmaze allows about 20 requests per 10 seconds per IP, so the script waits `--delay` seconds (default 0.5) after each call and retries with a growing pause if it receives HTTP 429.

## Data persistence
Results are written to a JSON file (`shows_sample.json` is a small committed example; other `shows*.json` files are git-ignored) and can be upserted into the `shows` table in Supabase (`schema.sql`). The TVmaze show id is the primary key, so re-loading updates rows instead of duplicating them. Same security model as the Books project: public read only, writes with the service-role key from `.env`.

## User interaction
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
cp .env.example .env   # only needed for the Supabase step
```
Tested with Python 3.13. Run `schema.sql` in the Supabase SQL Editor (safe to re-run) before `load_to_supabase.py`. `tvmaze.py` works without any configuration.

## Screenshot
TODO: add a screenshot of a terminal run.

## Learning
TODO (author).

## Limitations and assistance
- Only show-level data is stored; episodes, cast and schedules are not fetched.
- Tested end to end on 2026-11-25: live API fetch, `--test`, `--file shows_sample.json` (5 rows) and `--top 5` against Supabase.
- TODO (author): list AI tools used. This project was scaffolded with Claude Code, following the structure of the Books project.
