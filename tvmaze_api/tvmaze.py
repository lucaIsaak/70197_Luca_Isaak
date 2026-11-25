"""Small client for the public TVmaze API (https://www.tvmaze.com/api).

Usage:
    python tvmaze.py --search "office" --limit 5 --out shows.json
    python tvmaze.py --limit 20 --out shows.json      # first shows of the index

Fetches shows either by search term or from the paged show index, flattens each
show into a record, and writes a JSON list. Records match the `shows` table in
schema.sql. No API key is needed. TVmaze allows about 20 calls per 10 seconds
per IP, so requests are spaced by --delay and a 429 response is retried.
"""
import argparse
import json
import re
import time

import requests

BASE = "https://api.tvmaze.com"


def get_json(session, path, params=None, delay=0.5, retries=3):
    for attempt in range(retries + 1):
        r = session.get(BASE + path, params=params, timeout=20)
        if r.status_code == 429 and attempt < retries:
            wait = 2 ** (attempt + 1)  # back off: 2s, 4s, 8s
            print(f"Rate limited, waiting {wait}s ...")
            time.sleep(wait)
            continue
        r.raise_for_status()
        time.sleep(delay)
        return r.json()


def parse_show(s):
    network = s.get("network") or s.get("webChannel") or {}
    country = network.get("country") or {}
    summary = s.get("summary")
    return {
        "id": s["id"],
        "name": s["name"],
        "type": s.get("type"),
        "language": s.get("language"),
        "genres": s.get("genres") or [],
        "status": s.get("status"),
        "premiered": s.get("premiered"),
        "ended": s.get("ended"),
        "runtime": s.get("runtime") or s.get("averageRuntime"),
        "rating": (s.get("rating") or {}).get("average"),
        "network": network.get("name"),
        "country": country.get("name"),
        "official_site": s.get("officialSite"),
        "summary": re.sub(r"<[^>]+>", "", summary).strip() if summary else None,
        "image_url": (s.get("image") or {}).get("original"),
        "tvmaze_url": s.get("url"),
    }


def search(session, query, limit, delay):
    hits = get_json(session, "/search/shows", {"q": query}, delay)
    return [parse_show(h["show"]) for h in hits[:limit]]


def index(session, limit, delay):
    records, page = [], 0
    while len(records) < limit:
        try:
            shows = get_json(session, "/shows", {"page": page}, delay)
        except requests.HTTPError as e:
            if e.response.status_code == 404:  # past the last page
                break
            raise
        if not shows:
            break
        records += [parse_show(s) for s in shows[: limit - len(records)]]
        page += 1
    return records


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--search", help="search term; omit to read the show index")
    ap.add_argument("--limit", type=int, default=10)
    ap.add_argument("--delay", type=float, default=0.5)
    ap.add_argument("--out", default="shows.json")
    args = ap.parse_args()
    session = requests.Session()
    session.headers["User-Agent"] = "tvmaze-demo/0.1"
    if args.search:
        data = search(session, args.search, args.limit, args.delay)
    else:
        data = index(session, args.limit, args.delay)
    for i, r in enumerate(data, 1):
        print(f"[{i}/{len(data)}] {r['name']} ({r['premiered'] or '?'}) rating={r['rating']}")
    with open(args.out, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)
    print(f"Wrote {len(data)} records to {args.out}")
