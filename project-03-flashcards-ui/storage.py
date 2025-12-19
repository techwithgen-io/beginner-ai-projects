from __future__ import annotations

import json
import os
import time
from dataclasses import asdict, dataclass
from typing import Any, Dict, List


@dataclass
class Deck:
    id: str
    name: str
    topic: str
    difficulty: str
    cards: List[Dict[str, str]]  # [{"q": "...", "a": "..."}]
    created_at: float


def _ensure_dir(path: str) -> None:
    os.makedirs(path, exist_ok=True)


def _decks_path(memory_dir: str) -> str:
    _ensure_dir(memory_dir)
    return os.path.join(memory_dir, "decks.json")


def _stats_path(memory_dir: str) -> str:
    _ensure_dir(memory_dir)
    return os.path.join(memory_dir, "stats.json")


def _atomic_write_json(path: str, payload: Any) -> None:
    tmp = f"{path}.tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(payload, f, indent=2, ensure_ascii=False)
    os.replace(tmp, path)  # atomic on most OSes


def _normalize_cards(raw_cards: Any) -> List[Dict[str, str]]:
    if not isinstance(raw_cards, list):
        return []
    out: List[Dict[str, str]] = []
    for item in raw_cards:
        if not isinstance(item, dict):
            continue
        q = str(item.get("q", "")).strip()
        a = str(item.get("a", "")).strip()
        if q or a:
            out.append({"q": q, "a": a})
    return out


def load_decks(memory_dir: str) -> Dict[str, Deck]:
    path = _decks_path(memory_dir)
    if not os.path.exists(path):
        return {}

    with open(path, "r", encoding="utf-8") as f:
        raw = json.load(f)

    if not isinstance(raw, dict):
        return {}

    decks: Dict[str, Deck] = {}
    for deck_id, d in raw.items():
        if not isinstance(d, dict):
            continue

        created_at = d.get("created_at", time.time())
        try:
            created_at_f = float(created_at)
        except Exception:
            created_at_f = time.time()

        decks[str(deck_id)] = Deck(
            id=str(d.get("id", deck_id)),
            name=str(d.get("name", "Untitled Deck")),
            topic=str(d.get("topic", "")),
            difficulty=str(d.get("difficulty", "Beginner")),
            cards=_normalize_cards(d.get("cards")),
            created_at=created_at_f,
        )

    return decks


def save_decks(memory_dir: str, decks: Dict[str, Deck]) -> None:
    path = _decks_path(memory_dir)
    payload: Dict[str, Any] = {deck_id: asdict(deck) for deck_id, deck in decks.items()}
    _atomic_write_json(path, payload)


def upsert_deck(memory_dir: str, deck: Deck) -> None:
    decks = load_decks(memory_dir)
    decks[deck.id] = deck
    save_decks(memory_dir, decks)


def delete_deck(memory_dir: str, deck_id: str) -> bool:
    decks = load_decks(memory_dir)
    if deck_id not in decks:
        return False
    decks.pop(deck_id, None)
    save_decks(memory_dir, decks)
    return True


def load_stats(memory_dir: str) -> Dict[str, Any]:
    path = _stats_path(memory_dir)
    if not os.path.exists(path):
        return {"streak_days": 0, "last_study_date": None}

    try:
        with open(path, "r", encoding="utf-8") as f:
            raw = json.load(f)
        if not isinstance(raw, dict):
            return {"streak_days": 0, "last_study_date": None}
        return raw
    except Exception:
        return {"streak_days": 0, "last_study_date": None}


def save_stats(memory_dir: str, stats: Dict[str, Any]) -> None:
    path = _stats_path(memory_dir)
    _atomic_write_json(path, stats)
