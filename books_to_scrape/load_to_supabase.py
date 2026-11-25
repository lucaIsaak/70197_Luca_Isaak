"""Write scraped books to Supabase and read them back.

Setup:
    pip install supabase
    cp .env.example .env   # fill in SUPABASE_URL and SUPABASE_SERVICE_KEY

Usage:
    python load_to_supabase.py --test            # write+read+delete one dummy row
    python load_to_supabase.py --file books.json # upsert scraped data, then verify
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
    row = {"upc": "__test__", "title": "connection test", "price_gbp": 1.0,
           "product_url": "http://example.com"}
    sb.table("books").upsert(row).execute()
    got = sb.table("books").select("*").eq("upc", "__test__").execute().data
    assert got and got[0]["title"] == "connection test", "read-back failed"
    sb.table("books").delete().eq("upc", "__test__").execute()
    print("OK: wrote, read back, and deleted a test row.")


def load(sb, path):
    rows = json.load(open(path, encoding="utf-8"))
    sb.table("books").upsert(rows, on_conflict="upc").execute()
    back = sb.table("books").select("upc,title,price_gbp").in_(
        "upc", [r["upc"] for r in rows]).execute().data
    print(f"Upserted {len(rows)} rows; read back {len(back)}.")
    for r in back[:5]:
        print(" ", r)


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--test", action="store_true")
    ap.add_argument("--file")
    a = ap.parse_args()
    sb = client()
    if a.test:
        test_connection(sb)
    if a.file:
        load(sb, a.file)
