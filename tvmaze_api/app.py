"""Streamlit interface for the TVmaze project.

Usage:
    streamlit run app.py

Search view: searches TVmaze live and saves shows to the Supabase `shows` table.
My shows view: lists saved shows with filters, a chart and a detail view that
fetches the season and episode count live from TVmaze.

If Supabase is not configured or not reachable, the app shows the bundled
shows_sample.json read-only, so it can be tried without any keys.
"""
import json
import os

import pandas as pd
import requests
import streamlit as st

from load_to_supabase import load_env
from tvmaze import get_json, search

HERE = os.path.dirname(os.path.abspath(__file__))
SAMPLE = os.path.join(HERE, "shows_sample.json")


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
    sb.table("shows").upsert(show, on_conflict="id").execute()


def remove_show(sb, show_id):
    sb.table("shows").delete().eq("id", show_id).execute()


st.set_page_config(page_title="TVmaze shows", layout="wide")
st.title("TVmaze shows")

sb, error = supabase_client()
if sb:
    st.caption("Data source: TVmaze API (search) and Supabase table `shows` (your list)")
else:
    st.caption(f"Read-only demo: showing `shows_sample.json` (Supabase not used: {error}). "
               "Saving and removing are disabled.")

if "flash" in st.session_state:
    st.success(st.session_state.pop("flash"))

saved = load_saved(sb)
saved_ids = {s["id"] for s in saved}
# A radio keeps the chosen view across reruns (st.tabs jumps back to the first
# tab whenever a sidebar filter changes).
page = st.radio("View", ["Search", "My shows"], horizontal=True, key="page",
                label_visibility="collapsed",
                format_func=lambda p: f"My shows ({len(saved)})" if p == "My shows" else p)

# ---------- Search view: live TVmaze search ----------
if page == "Search":
    query = st.text_input("Search for a TV show", placeholder="e.g. office, dark, breaking bad")
    if query.strip():
        try:
            results = search_shows(query.strip())
        except requests.RequestException as e:
            st.error(f"TVmaze request failed: {e}")
            results = []
        if not results:
            st.info("No shows found.")
        for show in results:
            img, info, action = st.columns([1, 6, 1.4])
            if show["image_url"]:
                img.image(show["image_url"], width=90)
            info.markdown(f"**{show['name']}** ({(show['premiered'] or '?')[:4]})  ·  "
                          f"⭐ {show['rating'] or '–'}  ·  {', '.join(show['genres']) or 'no genre'}"
                          f"  ·  {show['network'] or 'unknown network'}")
            if show["summary"]:
                info.caption(show["summary"][:220] + ("…" if len(show["summary"]) > 220 else ""))
            if show["id"] in saved_ids:
                action.button("Saved ✓", key=f"s{show['id']}", disabled=True)
            elif action.button("Save", key=f"s{show['id']}", disabled=sb is None):
                save_show(sb, show)
                st.session_state["flash"] = f"Saved “{show['name']}” to your list."
                st.rerun()

# ---------- My shows view: saved shows from Supabase ----------
else:
    if not saved:
        st.info("Your list is empty. Search for a show and press Save.")
        st.stop()
    df = pd.DataFrame(saved)

    with st.sidebar:
        st.header("Filter my shows")
        genres = st.multiselect("Genre", sorted({g for gs in df["genres"] for g in gs}))
        min_rating = st.slider("Minimum rating", 0.0, 10.0, 0.0, 0.5)
        status = st.multiselect("Status", sorted(df["status"].dropna().unique()))

    view = df[df["rating"].fillna(0) >= min_rating]
    if genres:
        view = view[view["genres"].apply(lambda gs: any(g in gs for g in genres))]
    if status:
        view = view[view["status"].isin(status)]

    c1, c2, c3 = st.columns(3)
    c1.metric("Shows", len(view))
    c2.metric("Average rating", f"{view['rating'].mean():.1f}" if view["rating"].notna().any() else "–")
    c3.metric("Still running", int((view["status"] == "Running").sum()))

    st.dataframe(
        view[["name", "premiered", "rating", "genres", "network", "status", "tvmaze_url"]],
        hide_index=True,
        width="stretch",
        column_config={
            "name": "Show",
            "premiered": "Premiered",
            "rating": st.column_config.NumberColumn("Rating", format="%.1f"),
            "genres": st.column_config.ListColumn("Genres"),
            "network": "Network",
            "status": "Status",
            "tvmaze_url": st.column_config.LinkColumn("TVmaze", display_text="open"),
        },
    )

    if len(view):
        st.subheader("Shows per genre")
        counts = view["genres"].explode().dropna().value_counts()
        if len(counts):
            st.bar_chart(counts)

        st.subheader("Show details")
        # back to plain values: pandas turns missing numbers into NaN, which is truthy
        records = view.astype(object).where(view.notna(), None).to_dict("records")
        names = {f"{r['name']} ({(r['premiered'] or '?')[:4]})": r for r in records}
        show = names[st.selectbox("Choose a show", list(names))]
        left, right = st.columns([1, 3])
        if show.get("image_url"):
            left.image(show["image_url"])
        right.markdown(f"### {show['name']}")
        years = f"{(show['premiered'] or '?')[:4]}–{(show['ended'] or '')[:4]}"
        right.write(f"**{show['network'] or 'Unknown network'}**  ·  {years}  ·  {show['status']}  ·  "
                    f"⭐ {show['rating'] or '–'}  ·  {show['runtime'] or '?'} min")
        try:
            n_seasons, n_episodes, last = episode_stats(show["id"])
            right.write(f"**{n_seasons} season{'s' * (n_seasons != 1)}, {n_episodes} episodes**"
                        + (f" (latest aired {last})" if last else "") + "  ·  live from TVmaze")
        except requests.RequestException:
            right.write("Episode count unavailable (TVmaze not reachable).")
        right.write(show.get("summary") or "No summary.")
        right.markdown(f"[Open on TVmaze]({show['tvmaze_url']})")
        if right.button("Remove from my list", key=f"rm{show['id']}", disabled=sb is None):
            remove_show(sb, show["id"])
            st.session_state["flash"] = f"Removed “{show['name']}” from your list."
            st.rerun()
