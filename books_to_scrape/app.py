"""Streamlit interface for the scraped books.

Usage:
    streamlit run app.py

Reads the `books` table from Supabase when .env is configured. If Supabase is
not configured or not reachable, it falls back to the local JSON output of
scraper.py, so the interface can always be tried.
"""
import json
import os

import pandas as pd
import streamlit as st

from load_to_supabase import load_env

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_FILES = ["books100.json", "books.json"]  # first one that exists is used


@st.cache_data(ttl=300)
def load_books():
    load_env()
    if os.environ.get("SUPABASE_URL") and os.environ.get("SUPABASE_SERVICE_KEY"):
        try:
            from load_to_supabase import client
            rows = client().table("books").select("*").execute().data
            return pd.DataFrame(rows), "Supabase table `books`"
        except Exception as e:  # unreachable project, missing table, bad key ...
            error = type(e).__name__
    else:
        error = "no .env"
    for name in JSON_FILES:
        path = os.path.join(HERE, name)
        if os.path.exists(path):
            rows = json.load(open(path, encoding="utf-8"))
            return pd.DataFrame(rows), f"local file `{name}` (Supabase not used: {error})"
    return pd.DataFrame(), f"nothing found (Supabase not used: {error})"


st.set_page_config(page_title="Books to Scrape", layout="wide")
st.title("Books to Scrape")

df, source = load_books()
st.caption(f"Data source: {source}")
if df.empty:
    st.warning("No data yet. Run `python scraper.py --limit 20` first.")
    st.stop()

# Sidebar filters
with st.sidebar:
    st.header("Filter")
    query = st.text_input("Title contains")
    categories = st.multiselect("Category", sorted(df["category"].dropna().unique()))
    min_rating = st.slider("Minimum rating", 1, 5, 1)
    lo, hi = float(df["price_gbp"].min()), float(df["price_gbp"].max())
    price = st.slider("Price (GBP)", lo, hi, (lo, hi)) if lo < hi else (lo, hi)
    in_stock = st.checkbox("Only in stock")

view = df[(df["rating"].fillna(0) >= min_rating) & df["price_gbp"].between(*price)]
if query:
    view = view[view["title"].str.contains(query, case=False, na=False)]
if categories:
    view = view[view["category"].isin(categories)]
if in_stock:
    view = view[view["in_stock"]]

# Summary
c1, c2, c3 = st.columns(3)
c1.metric("Books", len(view))
c2.metric("Average price", f"£{view['price_gbp'].mean():.2f}" if len(view) else "–")
c3.metric("Average rating", f"{view['rating'].mean():.1f} / 5" if len(view) else "–")

# Table
cols = ["title", "category", "price_gbp", "rating", "stock_count", "product_url"]
st.dataframe(
    view[cols].sort_values("title"),
    hide_index=True,
    width="stretch",
    column_config={
        "title": "Title",
        "category": "Category",
        "price_gbp": st.column_config.NumberColumn("Price", format="£%.2f"),
        "rating": st.column_config.NumberColumn("Rating", format="%d ★"),
        "stock_count": "In stock",
        "product_url": st.column_config.LinkColumn("Link", display_text="open"),
    },
)

# Books per category
if len(view):
    st.subheader("Books per category")
    st.bar_chart(view["category"].value_counts())

# Detail view
if len(view):
    st.subheader("Book details")
    title = st.selectbox("Choose a book", sorted(view["title"]))
    book = view[view["title"] == title].iloc[0]
    left, right = st.columns([1, 3])
    if book.get("image_url"):
        left.image(book["image_url"])
    right.markdown(f"### {book['title']}")
    right.write(f"**Category:** {book['category']}  ·  **Price:** £{book['price_gbp']:.2f}  ·  "
                f"**Rating:** {int(book['rating'] or 0)} / 5  ·  **Stock:** {book['stock_count']}")
    right.write(book.get("description") or "No description.")
