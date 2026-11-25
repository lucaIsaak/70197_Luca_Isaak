"""Isolated scraper for https://books.toscrape.com.

Usage:
    python scraper.py --limit 10 --out books.json

Scrapes the catalogue list pages, then each book's detail page, and writes a
JSON list of records. Records match the `books` table in schema.sql.
"""
import argparse
import json
import re
import time
from urllib.parse import urljoin

import requests
from bs4 import BeautifulSoup

BASE = "https://books.toscrape.com/catalogue/"
START = BASE + "page-1.html"
RATINGS = {"One": 1, "Two": 2, "Three": 3, "Four": 4, "Five": 5}


def get_soup(session, url):
    r = session.get(url, timeout=20)
    r.raise_for_status()
    r.encoding = "utf-8"
    return BeautifulSoup(r.text, "html.parser")


def parse_book(soup, url):
    table = {
        row.th.get_text(strip=True): row.td.get_text(strip=True)
        for row in soup.select("table.table-striped tr")
    }
    stock_text = soup.select_one("p.availability").get_text(" ", strip=True)
    m = re.search(r"\((\d+) available\)", stock_text)
    rating_cls = soup.select_one("p.star-rating")["class"]
    crumbs = [a.get_text(strip=True) for a in soup.select("ul.breadcrumb li a")]
    desc = soup.select_one("#product_description")
    return {
        "upc": table["UPC"],
        "title": soup.select_one("h1").get_text(strip=True),
        "category": crumbs[-1] if len(crumbs) >= 3 else None,
        "price_gbp": float(re.sub(r"[^\d.]", "", table["Price (excl. tax)"])),
        "price_incl_tax_gbp": float(re.sub(r"[^\d.]", "", table["Price (incl. tax)"])),
        "tax_gbp": float(re.sub(r"[^\d.]", "", table["Tax"])),
        "in_stock": "In stock" in stock_text,
        "stock_count": int(m.group(1)) if m else 0,
        "rating": next((RATINGS[c] for c in rating_cls if c in RATINGS), None),
        "num_reviews": int(table["Number of reviews"]),
        "description": desc.find_next_sibling("p").get_text(strip=True) if desc else None,
        "image_url": urljoin(url, soup.select_one("#product_gallery img")["src"]),
        "product_url": url,
    }


def scrape(limit, delay):
    session = requests.Session()
    session.headers["User-Agent"] = "bookscrape-demo/0.1"
    records, page_url = [], START
    while page_url and len(records) < limit:
        listing = get_soup(session, page_url)
        for a in listing.select("article.product_pod h3 a"):
            if len(records) >= limit:
                break
            url = urljoin(page_url, a["href"])
            records.append(parse_book(get_soup(session, url), url))
            print(f"[{len(records)}/{limit}] {records[-1]['title']}")
            time.sleep(delay)
        nxt = listing.select_one("li.next a")
        page_url = urljoin(page_url, nxt["href"]) if nxt else None
    return records


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--out", default="books.json")
    args = ap.parse_args()
    data = scrape(args.limit, args.delay)
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(data)} records to {args.out}")
