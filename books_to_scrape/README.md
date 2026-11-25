# Books to Scrape

## Purpose
Scrapes book data from https://books.toscrape.com, stores it in a Supabase (Postgres) table, and presents it in a small Streamlit web app (`app.py`) with filters, summary numbers, a chart and a detail view.

## Data collection
`scraper.py` walks the catalogue list pages with `requests`, opens each book's detail page and parses it with BeautifulSoup (title, category, prices, stock, rating, reviews, description, image, URL). It waits `--delay` seconds (default 0.5) between pages to be polite to the site.

## Data persistence
Records are written to a JSON file (`books.json` is a 10-book sample) and then upserted into the `books` table in Supabase (`schema.sql`). The UPC is the primary key, so re-running the loader updates rows instead of duplicating them. Row level security allows public read only. The loader writes with the service-role key; the app only needs the read-only anon key (`SUPABASE_ANON_KEY`). Both live in `.env`, which is git-ignored.

## User interaction
Collect and store the data from the command line:
```bash
python scraper.py --limit 100 --out books100.json
python load_to_supabase.py --test
python load_to_supabase.py --file books100.json
```
Browse it in the web interface:
```bash
streamlit run app.py
```
The app opens at http://localhost:8501. The sidebar filters by title, category, minimum rating, price range and stock. The main page shows the number of matching books, average price and rating, a sortable table with links to each book, a chart of books per category, and a detail view with cover image and description.

The app reads the `books` table from Supabase when `.env` is set. If Supabase is not configured or not reachable, it falls back to the local `books100.json` (or the committed `books.json` sample) and says so at the top of the page, so the interface can be tried without a database.

## Setup
Tested with Python 3.13.
```bash
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env   # fill in SUPABASE_URL, SUPABASE_SERVICE_KEY and (optional) SUPABASE_ANON_KEY
```
Run `schema.sql` in the Supabase SQL Editor (safe to re-run), then the commands above. `streamlit run app.py` also works without `.env`: it then shows the local JSON data.

## Screenshot
TODO: add a screenshot of the terminal run and/or the Supabase table.

## Learning
TODO (author).

## Limitations and assistance
TODO (author): incomplete features and AI tools / tutorials used.
