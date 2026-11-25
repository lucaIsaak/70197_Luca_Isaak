"""Write TVmaze shows to Supabase and read them back.

Setup:
    pip install -r requirements.txt
    cp .env.example .env   # fill in SUPABASE_URL and SUPABASE_SERVICE_KEY
    # run schema.sql once in the Supabase SQL Editor

Usage:
    python load_to_supabase.py --test             # write+read+delete one dummy row
    python load_to_supabase.py --file shows.json  # upsert fetched shows, then verify
    python load_to_supabase.py --top 5            # list the best-rated stored shows
"""
import argparse
import json
import os

from supabase import create_client

ENV_PATH = os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env")


def load_env(path=ENV_PATH):
    # Look for .env next to this script, so it works from any working directory.
    if os.path.exists(path):
        for line in open(path):
            line = line.strip()
            if line and not line.startswith("#") and "=" in line:
                k, v = line.split("=", 1)
                os.environ.setdefault(k.strip(), v.strip())


def client():
    load_env()
    return create_client(os.environ["SUPABASE_URL"], os.environ["SUPABASE_SERVICE_KEY"])


def test_connection(sb):
    row = {"id": -1, "name": "connection test", "tvmaze_url": "http://example.com"}
    sb.table("shows").upsert(row).execute()
    try:
        got = sb.table("shows").select("*").eq("id", -1).execute().data
        assert got and got[0]["name"] == "connection test", "read-back failed"
    finally:  # never leave the dummy row behind
        sb.table("shows").delete().eq("id", -1).execute()
    print("OK: wrote, read back, and deleted a test row.")


def load(sb, path):
    rows = json.load(open(path, encoding="utf-8"))
    sb.table("shows").upsert(rows, on_conflict="id").execute()
    back = sb.table("shows").select("id,name,rating").in_(
        "id", [r["id"] for r in rows]).execute().data
    print(f"Upserted {len(rows)} rows; read back {len(back)}.")
    for r in back[:5]:
        print(" ", r)


def top(sb, n):
    rows = (sb.table("shows").select("name,premiered,rating,genres")
            .not_.is_("rating", "null").order("rating", desc=True).limit(n).execute().data)
    for r in rows:
        print(f"{r['rating']:>4}  {r['name']} ({r['premiered'] or '?'})  {', '.join(r['genres'])}")


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--file")
    ap.add_argument("--top", type=int)
    a = ap.parse_args()
    sb = client()
    if a.test:
        test_connection(sb)
    if a.file:
        load(sb, a.file)
    if a.top:
        top(sb, a.top)
