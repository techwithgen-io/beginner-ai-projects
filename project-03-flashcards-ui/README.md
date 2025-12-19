# Project 03 — Flashcards UI 🧠✨

A clean, interactive flashcard application built with **Streamlit** that lets users generate, study, and manage flashcards for any topic. The app focuses on a smooth study experience with progress tracking, streaks, and a tap-to-flip flashcard interface.

---

## 🚀 Overview

This project allows users to:

* Generate flashcards for any topic
* Study cards one at a time like a real deck
* Flip cards by tapping them
* Track progress, mastered cards, and daily study streaks
* Save decks locally and reuse them later

The goal of this project is to combine **good UX**, **clear learning flow**, and **AI-assisted content generation** without overengineering or unnecessary complexity.

---

## ✨ Features

* 📚 **Flashcard Generation** by topic and difficulty
* 🧠 **Study Mode** with tap-to-flip cards
* ✅ **Mastered Tracking** per study session
* 🔥 **Daily Study Streaks**
* 💾 **Local Deck Storage** (no accounts required)
* 📤 **Anki CSV Export**
* 🎨 **Clean, card-style UI** designed for focused studying

---

## 🤖 How AI Is Used in This Project

AI is used **only for generating flashcard content**.

An AI language model takes:

* A topic (e.g. `SQL joins`)
* A difficulty level (Beginner / Intermediate / Advanced)
* A number of cards

…and returns structured **question–answer pairs** that are saved and reused in the app.

All application logic, UI behavior, and state management are handled without AI.

---

## 💡 Why AI Is Used Here

Learning content is naturally flexible and topic-dependent.

Without AI, flashcards would need to be:

* Pre-written
* Limited to specific subjects
* Manually expanded over time

Using AI allows:

* Flashcards for **any topic**, not just predefined ones
* Easy scaling to new subjects (SQL, Python, Git, etc.)
* A reusable learning tool instead of a static quiz app

AI is applied **only where it adds real value** generating study material while everything else follows standard software engineering practices.

---

## 🛠️ Tech Stack

* **Frontend / App Framework:** Streamlit
* **Language:** Python
* **AI:** LLM-based flashcard generation
* **Storage:** Local file-based persistence
* **Export:** CSV (Anki-compatible)

---

## 📂 Project Structure

```
project-03-flashcards-ui/
├── app.py              # Main Streamlit app
├── agent.py            # AI flashcard generation logic
├── storage.py          # Local deck + stats persistence
├── memory/             # Saved decks and study stats
└── README.md
```

---

## ▶️ How to Run

```bash
pip install -r requirements.txt
streamlit run app.py
```

---

## 🎯 Design Philosophy

This project is intentionally built as a **hybrid of AI + traditional product engineering**:

* AI handles **content generation**
* The app handles **UX, state, persistence, and learning flow**

This mirrors how AI is typically integrated into real-world applications  as a tool, not a replacement for core logic.

---

Built by **Genesis** — Beginner AI Projects ✨


