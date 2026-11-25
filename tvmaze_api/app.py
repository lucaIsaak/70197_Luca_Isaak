"""Bingelist: a Streamlit interface for the TVmaze project.

Usage (from this folder, so the dark theme in .streamlit/config.toml is used):
    streamlit run app.py

Home:    a featured show and poster rows (trending, top rated, by genre) built
         from the first pages of the TVmaze show index.
Search:  live TVmaze search; Save adds a show to the Supabase `shows` table.
My list: your saved shows with filters, a detail view that fetches the season
         and episode count live from TVmaze, and Remove.

If Supabase is not configured or not reachable, the app shows the bundled
shows_sample.json as "My list" and disables saving, so it can be tried
without any keys.
"""
import html
import json
import os

import pandas as pd
import requests
import streamlit as st

from load_to_supabase import load_env
from tvmaze import get_json, parse_show, search

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "shows_sample.json")
INDEX_PAGES = 2   # each page of the TVmaze index has up to 250 shows
ROW_SIZE = 18     # posters per row on the Home page
GENRE_ROWS = ["Drama", "Comedy", "Crime", "Science-Fiction", "Thriller", "Action", "Horror", "Romance"]

CSS = """
<style>
#MainMenu, header[data-testid="stHeader"], footer {visibility: hidden; height: 0;}
.block-container {padding-top: 1.2rem; max-width: 1400px;}
.brand {font-size: 2.1rem; font-weight: 900; letter-spacing: .04em; color: #E23B3B; margin: 0;}
.brand-sub {color: #8c8c8c; font-size: .8rem; margin-top: -.2rem;}
.hero {position: relative; border-radius: 10px; overflow: hidden; min-height: 380px;
       background-size: cover; background-position: center 20%; margin: .6rem 0 1.4rem;}
.hero-shade {position: absolute; inset: 0;
       background: linear-gradient(90deg, #141414 0%, rgba(20,20,20,.88) 38%, rgba(20,20,20,.15) 75%),
                   linear-gradient(0deg, #141414 0%, rgba(20,20,20,0) 35%);}
.hero-body {position: relative; padding: 3rem 2.6rem; max-width: 560px;}
.hero-kicker {color: #E23B3B; font-weight: 700; font-size: .8rem; letter-spacing: .18em; text-transform: uppercase;}
.hero-title {font-size: 2.8rem; font-weight: 800; line-height: 1.05; margin: .3rem 0 .6rem; color: #fff;}
.hero-meta {color: #d2d2d2; font-size: .95rem; margin-bottom: .8rem;}
.hero-meta b {color: #46d369;}
.hero-text {color: #e5e5e5; font-size: .98rem; line-height: 1.45;
       display: -webkit-box; -webkit-line-clamp: 4; -webkit-box-orient: vertical; overflow: hidden;}
.row-title {font-size: 1.25rem; font-weight: 700; color: #e5e5e5; margin: 1.1rem 0 .45rem;}
.row {display: flex; gap: .55rem; overflow-x: auto; padding: .5rem .6rem 1rem; scrollbar-width: thin;}
.card {flex: 0 0 auto; width: 150px; text-decoration: none !important; color: #e5e5e5 !important;
       transition: transform .18s ease; display: block;}
.card:hover {transform: scale(1.07); z-index: 2;}
.card img {width: 150px; height: 211px; object-fit: cover; border-radius: 5px; display: block;
       box-shadow: 0 4px 14px rgba(0,0,0,.55);}
.card .noimg {width: 150px; height: 211px; border-radius: 5px; background: #2a2a2a; display: flex;
       align-items: center; justify-content: center; text-align: center; padding: .5rem; font-size: .85rem;}
.card .cap {font-size: .78rem; margin-top: .35rem; white-space: nowrap; overflow: hidden; text-overflow: ellipsis;}
.card .sub {font-size: .72rem; color: #8c8c8c;}
.card.fill {width: 100%;}
.card.fill img, .card.fill .noimg {width: 100%; height: auto; aspect-ratio: 210 / 295;}
.card.fill:hover {transform: scale(1.03);}
.grid {display: grid; grid-template-columns: repeat(auto-fill, minmax(150px, 1fr)); gap: 1rem .7rem;}
.pill {display: inline-block; border: 1px solid #555; border-radius: 3px; padding: 0 .4rem; margin-right: .35rem;
       font-size: .78rem; color: #cfcfcf;}
.stat {background: #1f1f1f; border-radius: 8px; padding: .8rem 1rem;}
.stat .n {font-size: 1.7rem; font-weight: 800; color: #fff;}
.stat .l {font-size: .78rem; color: #8c8c8c; text-transform: uppercase; letter-spacing: .08em;}
div[role="radiogroup"] label p {font-size: 1.02rem;}
</style>
"""


# ---------- data access ----------
@st.cache_resource
def supabase_client():
    """Return (client, None) if Supabase works, else (None, reason)."""
    load_env()
    url, key = os.environ.get("SUPABASE_URL"), os.environ.get("SUPABASE_SERVICE_KEY")
    if not (url and key):
        return None, "no .env"
    try:
        from supabase import create_client
        sb = create_client(url, key)
        sb.table("shows").select("id").limit(1).execute()  # fail early if unreachable
        return sb, None
    except Exception as e:
        return None, type(e).__name__


@st.cache_resource
def http():
    s = requests.Session()
    s.headers["User-Agent"] = "tvmaze-demo/0.1"
    return s


@st.cache_data(ttl=3600, show_spinner="Loading shows from TVmaze ...")
def index_pool(pages):
    """First pages of the TVmaze show index, with TVmaze's popularity weight."""
    pool = []
    for page in range(pages):
        for s in get_json(http(), "/shows", {"page": page}, delay=0.3):
            pool.append({**parse_show(s), "weight": s.get("weight") or 0})
    return pool


@st.cache_data(ttl=600, show_spinner="Searching TVmaze ...")
def search_shows(query):
    return search(http(), query, limit=10, delay=0.3)


@st.cache_data(ttl=3600, show_spinner="Loading episodes from TVmaze ...")
def episode_stats(show_id):
    episodes = get_json(http(), f"/shows/{show_id}/episodes", delay=0.3)
    seasons = {e["season"] for e in episodes}
    last = max((e["airdate"] for e in episodes if e.get("airdate")), default=None)
    return len(seasons), len(episodes), last


def load_saved(sb):
    if sb:
        return sb.table("shows").select("*").order("name").execute().data
    return json.load(open(SAMPLE, encoding="utf-8"))


def save_show(sb, show):
    row = {k: v for k, v in show.items() if k != "weight"}  # weight is not a table column
    sb.table("shows").upsert(row, on_conflict="id").execute()


def remove_show(sb, show_id):
    sb.table("shows").delete().eq("id", show_id).execute()


# ---------- small HTML helpers ----------
def poster(show):
    """Smaller poster version of TVmaze's original image (loads much faster)."""
    url = show.get("image_url")
    return url.replace("/original_untouched/", "/medium_portrait/") if url else None


def year(show):
    return (show.get("premiered") or "")[:4] or "?"


def card(show, fill=False):
    e = html.escape
    img = (f'<img src="{e(poster(show))}" alt="{e(show["name"])}" loading="lazy">' if poster(show)
           else f'<div class="noimg">{e(show["name"])}</div>')
    rating = f"★ {show['rating']}" if show.get("rating") else "no rating"
    return (f'<a class="card{" fill" if fill else ""}" href="{e(show.get("tvmaze_url") or "#")}" target="_blank">{img}'
            f'<div class="cap">{e(show["name"])}</div><div class="sub">{rating} · {year(show)}</div></a>')


def row(title, shows):
    if shows:
        st.markdown(f'<div class="row-title">{html.escape(title)}</div>'
                    f'<div class="row">{"".join(card(s) for s in shows)}</div>', unsafe_allow_html=True)


def hero(show, kicker):
    e = html.escape
    bg = f"background-image:url('{e(show['image_url'])}');" if show.get("image_url") else ""
    meta = [f"<b>★ {show['rating']}</b>" if show.get("rating") else "", year(show),
            e(show.get("network") or ""), e(", ".join(show.get("genres") or []))]
    st.markdown(
        f'<div class="hero" style="{bg}"><div class="hero-shade"></div><div class="hero-body">'
        f'<div class="hero-kicker">{e(kicker)}</div><div class="hero-title">{e(show["name"])}</div>'
        f'<div class="hero-meta">{" · ".join(m for m in meta if m)}</div>'
        f'<div class="hero-text">{e(show.get("summary") or "")}</div></div></div>',
        unsafe_allow_html=True)


def stat(col, number, label):
    col.markdown(f'<div class="stat"><div class="n">{number}</div><div class="l">{label}</div></div>',
                 unsafe_allow_html=True)


# ---------- page ----------
st.set_page_config(page_title="Bingelist · TVmaze", page_icon="📺", layout="wide")
st.markdown(CSS, unsafe_allow_html=True)

sb, error = supabase_client()
if "flash" in st.session_state:
    st.toast(st.session_state.pop("flash"))

saved = load_saved(sb)
saved_ids = {s["id"] for s in saved}

brand, nav = st.columns([2, 3], vertical_alignment="center")
brand.markdown('<p class="brand">BINGELIST</p><div class="brand-sub">powered by the TVmaze API</div>',
               unsafe_allow_html=True)
# A radio keeps the chosen page across reruns (st.tabs jumps back to the first
# tab whenever a widget changes).
page = nav.radio("Page", ["Home", "Search", "My list"], horizontal=True, key="page",
                 label_visibility="collapsed",
                 format_func=lambda p: f"My list ({len(saved)})" if p == "My list" else p)
if not sb:
    st.caption(f"Read-only demo: “My list” shows `shows_sample.json` (Supabase not used: {error}). "
               "Saving and removing are disabled.")


def save_button(show, key):
    if show["id"] in saved_ids:
        st.button("✓ In my list", key=key, disabled=True, use_container_width=True)
    elif st.button("＋ My list", key=key, disabled=sb is None, use_container_width=True, type="primary"):
        save_show(sb, show)
        st.session_state["flash"] = f"Added “{show['name']}” to your list."
        st.rerun()


# ---------- Home: featured show + poster rows ----------
if page == "Home":
    try:
        pool = [s for s in index_pool(INDEX_PAGES) if s.get("image_url")]
    except requests.RequestException as e:
        st.error(f"TVmaze request failed: {e}")
        st.stop()
    trending = sorted(pool, key=lambda s: (s["weight"], s["rating"] or 0), reverse=True)
    featured = next(s for s in trending if s.get("summary") and s.get("rating"))
    hero(featured, "Featured on TVmaze")
    c, _ = st.columns([1, 4])
    with c:
        save_button(featured, f"hero{featured['id']}")

    row(f"My list ({len(saved)})", saved[:ROW_SIZE])
    row("Trending on TVmaze", trending[:ROW_SIZE])
    top_rated = sorted(pool, key=lambda s: s["rating"] or 0, reverse=True)[:ROW_SIZE]
    row("Top rated", top_rated)
    # Genre rows skip shows already shown higher up, so the rows don't repeat each other.
    used = {s["id"] for s in trending[:ROW_SIZE] + top_rated}
    for genre in GENRE_ROWS:
        shows = [s for s in sorted(pool, key=lambda s: s["rating"] or 0, reverse=True)
                 if genre in s["genres"] and s["id"] not in used][:ROW_SIZE]
        if len(shows) >= 6:
            row(genre, shows)
            used |= {s["id"] for s in shows}
    st.caption(f"Home is built from the first {len(pool)} shows of the TVmaze index (with images). "
               "Use Search to find any of TVmaze's shows. Data: TVmaze, CC BY-SA 4.0.")

# ---------- Search: live TVmaze search ----------
elif page == "Search":
    query = st.text_input("Search", placeholder="Titles, e.g. dark, the office, breaking bad",
                          label_visibility="collapsed")
    if query.strip():
        try:
            results = search_shows(query.strip())
        except requests.RequestException as e:
            st.error(f"TVmaze request failed: {e}")
            results = []
        if not results:
            st.info("No shows found.")
        cols = st.columns(5)
        for i, show in enumerate(results):
            with cols[i % 5]:
                st.markdown(card(show, fill=True), unsafe_allow_html=True)
                save_button(show, f"s{show['id']}")
    else:
        st.markdown('<div class="row-title">Search TVmaze</div>', unsafe_allow_html=True)
        st.caption("Type a title above. Results come live from the TVmaze API (up to 10 per search).")

# ---------- My list: saved shows from Supabase ----------
else:
    if not saved:
        st.info("Your list is empty. Use Search or Home and press “＋ My list”.")
        st.stop()
    df = pd.DataFrame(saved)

    f1, f2, f3 = st.columns([3, 2, 2])
    genres = f1.multiselect("Genre", sorted({g for gs in df["genres"] for g in gs}))
    min_rating = f2.slider("Minimum rating", 0.0, 10.0, 0.0, 0.5)
    status = f3.multiselect("Status", sorted(df["status"].dropna().unique()))

    view = df[df["rating"].fillna(0) >= min_rating]
    if genres:
        view = view[view["genres"].apply(lambda gs: any(g in gs for g in genres))]
    if status:
        view = view[view["status"].isin(status)]
    # back to plain values: pandas turns missing numbers into NaN, which is truthy
    records = view.astype(object).where(view.notna(), None).to_dict("records")

    s1, s2, s3 = st.columns(3)
    stat(s1, len(view), "shows")
    stat(s2, f"{view['rating'].mean():.1f}" if view["rating"].notna().any() else "–", "average rating")
    stat(s3, int((view["status"] == "Running").sum()), "still running")

    st.markdown(f'<div class="row-title">My list</div><div class="grid">{"".join(card(s, fill=True) for s in records)}</div>',
                unsafe_allow_html=True)

    if records:
        st.markdown('<div class="row-title">Details</div>', unsafe_allow_html=True)
        names = {f"{r['name']} ({year(r)})": r for r in records}
        show = names[st.selectbox("Choose a show", list(names), label_visibility="collapsed")]
        hero(show, "From your list")
        info, action = st.columns([4, 1])
        years = f"{year(show)}–{(show.get('ended') or '')[:4]}"
        pills = "".join(f'<span class="pill">{html.escape(p)}</span>' for p in
                        [show.get("status") or "", years, f"{show.get('runtime') or '?'} min"] if p)
        try:
            n_seasons, n_episodes, last = episode_stats(show["id"])
            episodes = (f"<b>{n_seasons} season{'s' * (n_seasons != 1)} · {n_episodes} episodes</b>"
                        + (f" · latest aired {last}" if last else "") + " · live from TVmaze")
        except requests.RequestException:
            episodes = "Episode count unavailable (TVmaze not reachable)."
        info.markdown(f"{pills}<br><br>{episodes}<br><br>"
                      f"<a href='{html.escape(show['tvmaze_url'])}' target='_blank'>Open on TVmaze ↗</a>",
                      unsafe_allow_html=True)
        if action.button("Remove from my list", key=f"rm{show['id']}", disabled=sb is None,
                         use_container_width=True):
            remove_show(sb, show["id"])
            st.session_state["flash"] = f"Removed “{show['name']}” from your list."
            st.rerun()

        with st.expander("Stats: shows per genre"):
            counts = view["genres"].explode().dropna().value_counts()
            if len(counts):
                st.bar_chart(counts, color="#E23B3B")
