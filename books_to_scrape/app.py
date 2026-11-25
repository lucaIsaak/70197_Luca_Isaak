"""Bookshelf: a Streamlit interface for the scraped books.

Usage (from this folder, so the dark theme in .streamlit/config.toml is used):
    streamlit run app.py

Home:   a featured book and cover rows (five-star books, good value, by category).
Browse: filters (title, category, rating, price, stock), a cover grid, a detail
        view and the full table.

Reads the `books` table from Supabase when .env is configured (preferably with
the read-only SUPABASE_ANON_KEY). If Supabase is not configured or not
reachable, it falls back to the local JSON output of scraper.py, so the
interface can always be tried.
"""
import html
import json
import os

import pandas as pd
import streamlit as st

from load_to_supabase import load_env

HERE = os.path.dirname(os.path.abspath(__file__))
JSON_FILES = ["books100.json", "books.json"]  # first one that exists is used
ROW_SIZE = 18

CSS = """
<style>
#MainMenu, header[data-testid="stHeader"], footer {visibility: hidden; height: 0;}
.block-container {padding-top: 1.2rem; max-width: 1400px;}
.brand {font-size: 2.1rem; font-weight: 900; letter-spacing: .04em; color: #E23B3B; margin: 0;}
.brand-sub {color: #8c8c8c; font-size: .8rem; margin-top: -.2rem;}
.hero {position: relative; display: flex; gap: 2.2rem; align-items: center; border-radius: 10px;
       overflow: hidden; padding: 2.4rem 2.6rem; margin: .6rem 0 1.4rem; min-height: 340px;}
.hero-bg {position: absolute; inset: -40px; background-size: cover; background-position: center;
       filter: blur(28px) brightness(.45); transform: scale(1.1);}
.hero-shade {position: absolute; inset: 0; background: linear-gradient(90deg, rgba(20,20,20,.25), #141414 85%);}
.hero img {position: relative; height: 280px; border-radius: 6px; box-shadow: 0 10px 30px rgba(0,0,0,.7);}
.hero-body {position: relative; max-width: 640px;}
.hero-kicker {color: #E23B3B; font-weight: 700; font-size: .8rem; letter-spacing: .18em; text-transform: uppercase;}
.hero-title {font-size: 2.4rem; font-weight: 800; line-height: 1.08; margin: .3rem 0 .6rem; color: #fff;}
.hero-meta {color: #d2d2d2; font-size: .95rem; margin-bottom: .8rem;}
.hero-meta b {color: #f5c518;}
.hero-text {color: #e5e5e5; font-size: .96rem; line-height: 1.45;
       display: -webkit-box; -webkit-line-clamp: 5; -webkit-box-orient: vertical; overflow: hidden;}
.row-title {font-size: 1.25rem; font-weight: 700; color: #e5e5e5; margin: 1.1rem 0 .45rem;}
.row {display: flex; gap: .55rem; overflow-x: auto; padding: .5rem .6rem 1rem; scrollbar-width: thin;}
.card {flex: 0 0 auto; width: 140px; text-decoration: none !important; color: #e5e5e5 !important;
       transition: transform .18s ease; display: block;}
.card:hover {transform: scale(1.07); z-index: 2;}
.card img {width: 140px; height: 205px; object-fit: cover; border-radius: 4px; display: block;
       box-shadow: 0 4px 14px rgba(0,0,0,.55); background: #2a2a2a;}
.card.fill {width: 100%;}
.card.fill img {width: 100%; height: auto; aspect-ratio: 140 / 205;}
.card.fill:hover {transform: scale(1.03);}
.card .cap {font-size: .78rem; margin-top: .35rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.card .sub {font-size: .72rem; color: #8c8c8c;}
.card .sub b {color: #f5c518; font-weight: 400;}
.grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(140px, 1fr)); gap: 1rem .7rem;}
.pill {display: inline-block; border: 1px solid #555; border-radius: 3px; padding: 0 .4rem; margin-right: .35rem;
       font-size: .78rem; color: #cfcfcf;}
.stat {background: #1f1f1f; border-radius: 8px; padding: .8rem 1rem;}
.stat .n {font-size: 1.7rem; font-weight: 800; color: #fff;}
.stat .l {font-size: .78rem; color: #8c8c8c; text-transform: uppercase; letter-spacing: .08em;}
div[role="radiogroup"] label p {font-size: 1.02rem;}
</style>
"""


@st.cache_data(ttl=300)
def load_books():
    load_env()
    # Reading only needs the public anon key (RLS allows read-only access).
    # The service-role key is used only as a fallback for local use.
    url = os.environ.get("SUPABASE_URL")
    key = os.environ.get("SUPABASE_ANON_KEY") or os.environ.get("SUPABASE_SERVICE_KEY")
    if url and key:
        try:
            from supabase import create_client
            rows = create_client(url, key).table("books").select("*").execute().data
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


# ---------- small HTML helpers ----------
def stars(n):
    n = int(n or 0)
    return "★" * n + "☆" * (5 - n)


def card(book, fill=False):
    e = html.escape
    return (f'<a class="card{" fill" if fill else ""}" href="{e(book["product_url"])}" target="_blank">'
            f'<img src="{e(book.get("image_url") or "")}" alt="{e(book["title"])}" loading="lazy">'
            f'<div class="cap">{e(book["title"])}</div>'
            f'<div class="sub"><b>{stars(book["rating"])}</b> · £{book["price_gbp"]:.2f}</div></a>')


def row(title, books):
    if books:
        st.markdown(f'<div class="row-title">{html.escape(title)}</div>'
                    f'<div class="row">{"".join(card(b) for b in books)}</div>', unsafe_allow_html=True)


def hero(book, kicker):
    e = html.escape
    img = e(book.get("image_url") or "")
    stock = f"{book['stock_count']} in stock" if book.get("in_stock") else "out of stock"
    st.markdown(
        f'<div class="hero"><div class="hero-bg" style="background-image:url(\'{img}\')"></div>'
        f'<div class="hero-shade"></div><img src="{img}" alt="">'
        f'<div class="hero-body"><div class="hero-kicker">{e(kicker)}</div>'
        f'<div class="hero-title">{e(book["title"])}</div>'
        f'<div class="hero-meta"><b>{stars(book["rating"])}</b> · £{book["price_gbp"]:.2f} · '
        f'{e(book.get("category") or "")} · {stock}</div>'
        f'<div class="hero-text">{e(book.get("description") or "No description.")}</div></div></div>',
        unsafe_allow_html=True)


def stat(col, number, label):
    col.markdown(f'<div class="stat"><div class="n">{number}</div><div class="l">{label}</div></div>',
                 unsafe_allow_html=True)


# ---------- page ----------
st.set_page_config(page_title="Bookshelf · Books to Scrape", page_icon="📚", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

df, source = load_books()
brand, nav = st.columns([2, 3], vertical_alignment="center")
brand.markdown('<p class="brand">BOOKSHELF</p><div class="brand-sub">scraped from books.toscrape.com</div>',
               unsafe_allow_html=True)
page = nav.radio("Page", ["Home", "Browse"], horizontal=True, key="page", label_visibility="collapsed")

if df.empty:
    st.warning("No data yet. Run `python scraper.py --limit 20` first.")
    st.stop()
books = df.astype(object).where(df.notna(), None).to_dict("records")

# ---------- Home: featured book + cover rows ----------
if page == "Home":
    five = sorted((b for b in books if b["rating"] == 5), key=lambda b: -b["price_gbp"])
    featured = next((b for b in five if b.get("description")), books[0])
    hero(featured, "Featured five-star book")

    row("Five stars", five[:ROW_SIZE])
    row("Great value: 4+ stars under £25",
        sorted((b for b in books if (b["rating"] or 0) >= 4 and b["price_gbp"] < 25),
               key=lambda b: b["price_gbp"])[:ROW_SIZE])
    for category, count in df["category"].value_counts().items():
        # "Default" and "Add a comment" are placeholder categories on books.toscrape.com
        if count >= 4 and category not in ("Default", "Add a comment"):
            row(category, sorted((b for b in books if b["category"] == category),
                                 key=lambda b: -(b["rating"] or 0))[:ROW_SIZE])
    st.caption(f"{len(books)} books · data source: {source}. Click a cover to open the book on books.toscrape.com.")

# ---------- Browse: filters, grid, details, table ----------
else:
    f1, f2, f3, f4 = st.columns([3, 3, 2, 2])
    query = f1.text_input("Title contains", placeholder="e.g. light")
    categories = f2.multiselect("Category", sorted(df["category"].dropna().unique()))
    min_rating = f3.slider("Minimum rating", 1, 5, 1)
    lo, hi = float(df["price_gbp"].min()), float(df["price_gbp"].max())
    price = f4.slider("Price (£)", lo, hi, (lo, hi)) if lo < hi else (lo, hi)
    in_stock = st.checkbox("Only in stock")

    view = df[(df["rating"].fillna(0) >= min_rating) & df["price_gbp"].between(*price)]
    if query:
        view = view[view["title"].str.contains(query, case=False, na=False)]
    if categories:
        view = view[view["category"].isin(categories)]
    if in_stock:
        view = view[view["in_stock"]]
    records = view.astype(object).where(view.notna(), None).sort_values("title").to_dict("records")

    s1, s2, s3 = st.columns(3)
    stat(s1, len(view), "books")
    stat(s2, f"£{view['price_gbp'].mean():.2f}" if len(view) else "–", "average price")
    stat(s3, f"{view['rating'].mean():.1f} / 5" if len(view) else "–", "average rating")

    if not records:
        st.info("No books match these filters.")
        st.stop()
    st.markdown(f'<div class="row-title">Books</div><div class="grid">{"".join(card(b, fill=True) for b in records)}</div>',
                unsafe_allow_html=True)

    st.markdown('<div class="row-title">Details</div>', unsafe_allow_html=True)
    titles = [b["title"] for b in records]
    book = records[titles.index(st.selectbox("Choose a book", titles, label_visibility="collapsed"))]
    hero(book, book.get("category") or "Book")
    st.markdown(f'<span class="pill">UPC {html.escape(book["upc"])}</span>'
                f'<span class="pill">£{book["price_gbp"]:.2f} excl. tax · £{(book.get("price_incl_tax_gbp") or book["price_gbp"]):.2f} incl. tax</span>'
                f'<span class="pill">{book.get("num_reviews") or 0} reviews</span>'
                f' &nbsp; <a href="{html.escape(book["product_url"])}" target="_blank">Open on books.toscrape.com ↗</a>',
                unsafe_allow_html=True)

    with st.expander("All matching books as a table, and books per category"):
        st.dataframe(
            view[["title", "category", "price_gbp", "rating", "stock_count", "product_url"]].sort_values("title"),
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
        st.bar_chart(view["category"].value_counts(), color="#E23B3B")
    st.caption(f"Data source: {source}")
