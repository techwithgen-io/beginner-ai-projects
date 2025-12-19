from __future__ import annotations

import csv
import time
from datetime import date, datetime, timedelta
from io import StringIO
from typing import Any

import streamlit as st

from agent import generate_flashcards, shuffle_cards
from storage import Deck, delete_deck, load_decks, load_stats, save_stats, upsert_deck


APP_TITLE = "Project 03 — Flashcards UI"
MEMORY_DIR = "memory"

QUICK_TOPICS = [
    "SQL joins",
    "Python lists",
    "Python dictionaries",
    "OOP basics",
    "Git basics",
    "AI agents (ReAct)",
    "LangChain basics",
]


def inject_css() -> None:
    st.markdown(
        """
<style>
:root{
  --pink: rgba(255, 92, 168, 0.96);
  --pink2: rgba(255, 138, 200, 0.60);
  --pink-soft: rgba(255, 92, 168, 0.22);
}

/* Flashcard centering */
div:has(#flashcard-anchor) + div {
  display: flex;
  justify-content: center;
}

/* Flashcard button only */
div:has(#flashcard-anchor) + div button {
  max-width: 880px !important;
  width: 100% !important;

  margin-left: auto !important;
  margin-right: auto !important;
  display: block !important;

  padding: 48px 44px !important;
  border-radius: 14px !important;

  border: 2px solid rgba(255, 92, 168, 0.65) !important;

  background:
    linear-gradient(135deg,
      rgba(255, 92, 168, 0.18),
      rgba(18, 20, 28, 0.92)) !important;

  box-shadow:
    0 24px 70px rgba(0,0,0,0.55),
    0 0 0 1px rgba(255, 92, 168, 0.18) inset !important;

  color: rgba(255,255,255,0.96) !important;
  text-align: center !important;
  white-space: pre-wrap !important;
  line-height: 1.35 !important;
  font-weight: 800 !important;

  transition: transform .12s ease, box-shadow .14s ease, border-color .14s ease;
}

div:has(#flashcard-anchor) + div button:hover{
  border-color: rgba(255, 92, 168, 0.95) !important;
  box-shadow:
    0 32px 90px rgba(0,0,0,0.65),
    0 0 45px rgba(255, 92, 168, 0.22) !important;
  transform: translateY(-2px);
}

div:has(#flashcard-anchor) + div button:active{
  transform: scale(0.995);
}

.app-title-wrap{
  text-align:center;
  margin-bottom: 6px;
}
.app-title-wrap h2{
  margin: 0;
}
.app-title-sub{
  opacity: 0.75;
  font-size: 14px;
  margin-top: 6px;
}
</style>
""",
        unsafe_allow_html=True,
    )


def cute_deck_name(topic: str) -> str:
    t = (topic or "").strip()
    return t if t else "Flashcards"


def set_page(page: str) -> None:
    st.session_state.page = page


def ensure_state() -> None:
    st.session_state.setdefault("page", "Create")
    st.session_state.setdefault("selected_deck_id", None)

    st.session_state.setdefault("study_index", 0)
    st.session_state.setdefault("study_revealed", False)
    st.session_state.setdefault("study_mastered_ids", set())

    st.session_state.setdefault("create_topic", "")
    st.session_state.setdefault("create_difficulty", "Intermediate")
    st.session_state.setdefault("create_n", 5)


def update_streak_on_study(memory_dir: str) -> None:
    stats = load_stats(memory_dir)
    last = stats.get("last_study_date")
    streak = int(stats.get("streak_days", 0) or 0)

    today = date.today().isoformat()
    if last == today:
        return

    last_dt = None
    if last:
        try:
            last_dt = datetime.fromisoformat(last).date()
        except Exception:
            last_dt = None

    if last_dt is None:
        streak = 1
    else:
        streak = streak + 1 if (date.today() - last_dt == timedelta(days=1)) else 1

    stats["streak_days"] = streak
    stats["last_study_date"] = today
    save_stats(memory_dir, stats)


def anki_csv_bytes(deck: Deck) -> bytes:
    output = StringIO()
    writer = csv.writer(output)
    for c in deck.cards:
        writer.writerow([c.get("q", ""), c.get("a", "")])
    return output.getvalue().encode("utf-8")


def render_header(memory_dir: str) -> None:
    stats = load_stats(memory_dir)
    streak_days = int(stats.get("streak_days", 0) or 0)

    st.markdown(
        f"""
<div class="app-title-wrap">
  <h2>💖 {APP_TITLE}</h2>
  <div class="app-title-sub">Generate flashcards → study like a real deck → save locally</div>
</div>
""",
        unsafe_allow_html=True,
    )

    st.markdown(f"🔥 **Streak:** {streak_days} day(s)")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.button("✨ Create", use_container_width=True, on_click=set_page, args=("Create",), key="nav_create")
    with c2:
        st.button("📁 My Decks", use_container_width=True, on_click=set_page, args=("My Decks",), key="nav_decks")
    with c3:
        st.button("🧠 Study", use_container_width=True, on_click=set_page, args=("Study",), key="nav_study")

    st.divider()


def render_create(memory_dir: str) -> None:
    st.markdown("### ✨ Create flashcards")
    st.caption("Quick topics:")

    cols = st.columns(4)
    for i, topic in enumerate(QUICK_TOPICS):
        with cols[i % 4]:
            if st.button(topic, key=f"qt_{i}", use_container_width=True):
                st.session_state.create_topic = topic

    st.caption(f"Deck name (auto): **{cute_deck_name(st.session_state.create_topic)}**")

    st.text_input("Topic", key="create_topic", placeholder="e.g. SQL LEFT JOIN vs INNER JOIN")
    st.selectbox("Difficulty", ["Beginner", "Intermediate", "Advanced"], key="create_difficulty")
    st.number_input("Number of cards", min_value=1, max_value=50, step=1, key="create_n")

    if st.button("💖 Generate & Save", use_container_width=True, key="btn_generate_save"):
        topic = (st.session_state.create_topic or "").strip()
        if not topic:
            st.warning("Type a topic (or tap a quick topic).")
            return

        deck_name = cute_deck_name(topic)
        difficulty = st.session_state.create_difficulty
        n = int(st.session_state.create_n)

        cards = generate_flashcards(topic=topic, difficulty=difficulty, n=n)
        card_dicts = [{"q": c.q, "a": c.a} for c in cards]

        deck_id = f"deck_{int(time.time() * 1000)}"
        deck = Deck(
            id=deck_id,
            name=deck_name,
            topic=topic,
            difficulty=difficulty,
            cards=card_dicts,
            created_at=time.time(),
        )
        upsert_deck(memory_dir, deck)

        st.session_state.selected_deck_id = deck_id
        st.session_state.page = "My Decks"
        st.rerun()  # <-- this is the one rerun we actually want


def render_decks(memory_dir: str) -> None:
    st.markdown("### 📁 My Decks")

    decks = load_decks(memory_dir)
    if not decks:
        st.info("No decks yet. Go to **Create** to make one.")
        return

    ordered = sorted(decks.values(), key=lambda d: d.created_at, reverse=True)

    for deck in ordered:
        st.markdown(f"#### {deck.name}")
        st.caption(f"{deck.topic} • {deck.difficulty} • {len(deck.cards)} cards")

        left, mid, right = st.columns([3, 2, 3])

        with left:
            if st.button("🧠 Study", key=f"study_{deck.id}", use_container_width=True):
                st.session_state.selected_deck_id = deck.id
                st.session_state.study_index = 0
                st.session_state.study_revealed = False
                st.session_state.study_mastered_ids = set()
                st.session_state.page = "Study"
                st.rerun()

        with mid:
            st.download_button(
                "📥 Export Anki CSV",
                data=anki_csv_bytes(deck),
                file_name=f"{deck.name}.csv",
                mime="text/csv",
                key=f"anki_{deck.id}",
                use_container_width=True,
            )

        with right:
            if st.button("🗑️ Delete", key=f"del_{deck.id}", use_container_width=True):
                if delete_deck(memory_dir, deck.id):
                    if st.session_state.get("selected_deck_id") == deck.id:
                        st.session_state.selected_deck_id = None
                    st.rerun()

        st.divider()


def render_study(memory_dir: str) -> None:
    decks = load_decks(memory_dir)
    deck_id = st.session_state.get("selected_deck_id")

    if not deck_id or deck_id not in decks:
        st.info("Pick a deck from **My Decks** first.")
        return

    deck = decks[deck_id]
    cards = deck.cards or []
    if not cards:
        st.warning("This deck has no cards.")
        return

    update_streak_on_study(memory_dir)

    total = len(cards)
    idx = int(st.session_state.get("study_index", 0)) % total
    st.session_state.study_index = idx

    st.markdown("### 🧠 Study mode")

    left_info, right_info = st.columns([1, 1])
    with left_info:
        st.markdown(f"**Studying:** {deck.topic}")
    with right_info:
        st.markdown(
            f"<div style='text-align:right; opacity:0.75; font-size:14px;'>"
            f"{deck.difficulty} • Card {idx+1}/{total}"
            f"</div>",
            unsafe_allow_html=True,
        )

    mastered_set = st.session_state.get("study_mastered_ids", set())
    if not isinstance(mastered_set, set):
        mastered_set = set()
        st.session_state.study_mastered_ids = mastered_set

    st.progress((idx + 1) / total)
    st.caption(f"✅ Mastered: {len(mastered_set)}/{total}")

    q = (cards[idx].get("q", "") or "").strip()
    a = (cards[idx].get("a", "") or "").strip()
    revealed = bool(st.session_state.get("study_revealed", False))

    st.markdown('<div id="flashcard-anchor"></div>', unsafe_allow_html=True)

    card_text = a if revealed else q
    if st.button(f"{card_text}\n\n✨ Tap to flip", key=f"card_{deck.id}_{idx}_{'a' if revealed else 'q'}", use_container_width=True):
        st.session_state.study_revealed = not revealed

    st.markdown("")

    c1, c2, c3, c4 = st.columns([2, 3, 2, 2])

    with c1:
        if st.button("← Prev", key=f"prev_{deck.id}_{idx}", use_container_width=True):
            st.session_state.study_index = (idx - 1) % total
            st.session_state.study_revealed = False

    with c2:
        if st.button("✅ Got it", key=f"master_{deck.id}_{idx}", use_container_width=True):
            mastered_set.add(idx)
            st.session_state.study_mastered_ids = mastered_set
            st.session_state.study_revealed = False
            st.session_state.study_index = (idx + 1) % total

    with c3:
        if st.button("Next →", key=f"next_{deck.id}_{idx}", use_container_width=True):
            st.session_state.study_index = (idx + 1) % total
            st.session_state.study_revealed = False

    with c4:
        if st.button("❌ Exit", key=f"exit_{deck.id}_{idx}", use_container_width=True):
            st.session_state.study_revealed = False
            st.session_state.page = "My Decks"
            st.rerun()

    st.caption("Built by Genesis — Beginner AI Projects ✨")


def main() -> None:
    st.set_page_config(page_title=APP_TITLE, layout="wide")
    inject_css()
    ensure_state()

    render_header(MEMORY_DIR)

    page = st.session_state.get("page", "Create")
    if page == "Create":
        render_create(MEMORY_DIR)
    elif page == "My Decks":
        render_decks(MEMORY_DIR)
    else:
        render_study(MEMORY_DIR)


if __name__ == "__main__":
    main()
