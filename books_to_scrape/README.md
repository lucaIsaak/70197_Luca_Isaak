# Books to Scrape

## Purpose
Scrapes book data from https://books.toscrape.com, stores it in a Supabase (Postgres) table, and reads it back.

## Data collection
`scraper.py` walks the catalogue list pages with `requests`, opens each book's detail page and parses it with BeautifulSoup (title, category, prices, stock, rating, reviews, description, image, URL). It waits `--delay` seconds (default 0.5) between pages to be polite to the site.

## Data persistence
Records are written to a JSON file (`books.json` is a 10-book sample) and then upserted into the `books` table in Supabase (`schema.sql`). The UPC is the primary key, so re-running the loader updates rows instead of duplicating them. Row level security allows public read only; writes use the service-role key from `.env`, which is never committed.

## User interaction
Command line:
```bash
python scraper.py --limit 10 --out books.json
python load_to_supabase.py --test
python load_to_supabase.py --file books.json
```
TODO (author): the assignment asks for an interface to present the data. Describe it here (e.g. the Supabase table editor, or a small app).

## Setup
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SUPABASE_URL and SUPABASE_SERVICE_KEY
```
Run `schema.sql` once in the Supabase SQL Editor, then the commands above.

## Screenshot
TODO: add a screenshot of the terminal run and/or the Supabase table.

## Learning
TODO (author).

## Limitations and assistance
TODO (author): incomplete features and AI tools / tutorials used.
