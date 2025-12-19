from __future__ import annotations

import os
import random
import json
import re
from dataclasses import dataclass
from typing import List, Dict

from dotenv import load_dotenv

try:
    from langchain_openai import ChatOpenAI  # type: ignore
except Exception:
    ChatOpenAI = None  # type: ignore

load_dotenv()


@dataclass
class Flashcard:
    q: str
    a: str


SYSTEM_STYLE = """You are a friendly, focused flashcard generator.
Rules:
- Keep questions short and specific.
- Keep answers short and correct.
- Avoid fluff.
- Use simple language if the user is a beginner.
Return JSON only in this schema:
{"cards":[{"q":"...","a":"..."}]}
"""


def _fallback_cards(topic: str, difficulty: str, n: int) -> List[Flashcard]:
    topic_clean = topic.strip() or "your topic"
    cards: List[Flashcard] = []
    for i in range(1, n + 1):
        cards.append(
            Flashcard(
                q=f"What is {topic_clean}? (Q{i} • {difficulty})",
                a=f"A short definition/idea for {topic_clean}.",
            )
        )
    return cards


def _extract_json_object(text: str) -> dict:
    text = (text or "").strip()
    try:
        return json.loads(text)
    except Exception:
        pass

    m = re.search(r"\{[\s\S]*\}", text)
    if not m:
        raise ValueError("No JSON object found in model output.")
    return json.loads(m.group(0))


def generate_flashcards(topic: str, difficulty: str, n: int) -> List[Flashcard]:
    topic = (topic or "").strip()
    difficulty = (difficulty or "Beginner").strip()
    n = max(1, min(int(n), 50))

    api_key = os.getenv("OPENAI_API_KEY", "").strip()
    if not api_key or ChatOpenAI is None:
        return _fallback_cards(topic, difficulty, n)

    llm = ChatOpenAI(model="gpt-4o-mini", temperature=0.4)

    prompt = f"""
Create {n} flashcards about: {topic}
Difficulty: {difficulty}
Return valid JSON only:
{{"cards":[{{"q":"...","a":"..."}}]}}
""".strip()

    try:
        msg = llm.invoke([("system", SYSTEM_STYLE), ("user", prompt)])
        text = getattr(msg, "content", "") or ""
        data = _extract_json_object(text)

        raw_cards = data.get("cards", [])
        cards: List[Flashcard] = []

        if isinstance(raw_cards, list):
            for c in raw_cards:
                if not isinstance(c, dict):
                    continue
                q = str(c.get("q", "")).strip()
                a = str(c.get("a", "")).strip()
                if q and a:
                    cards.append(Flashcard(q=q, a=a))

        return cards[:n] if cards else _fallback_cards(topic, difficulty, n)
    except Exception:
        return _fallback_cards(topic, difficulty, n)


def shuffle_cards(cards: List[Dict[str, str]]) -> List[Dict[str, str]]:
    out = list(cards)
    random.shuffle(out)
    return out
