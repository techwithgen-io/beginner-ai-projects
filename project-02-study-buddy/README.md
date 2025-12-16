# Project 02 — Context-Aware AI Study Buddy 🧠📚

This is **Project 02** in the **Beginner AI Projects** series.

In this project, we build a **command-line Study Buddy** that **remembers your learning context** (your name, what you’re learning, your level, and preferences) and uses it to respond like a personalized tutor.

The goal is to teach beginners what “AI memory” actually means — **without a UI** or extra complexity.

---

## 🧠 What You’ll Learn

* What “memory” means in an AI agent (not just chat history)
* How to store and load memory locally using a JSON file
* How to personalize responses using saved context
* How to safely manage API keys using `.env`
* How to run a multi-project repo using `uv`

---

## 🛠 Tech Stack

* Python
* LangChain
* OpenAI API
* `rich` (better CLI output)
* `uv` (dependency management)

---

## 📂 Project Structure

```
project-02-study-buddy/
├─ main.py
├─ README.md
├─ pyproject.toml
├─ uv.lock
├─ .env.example
├─ memory/
│  └─ user_profile.json
```

---

## 🚀 Getting Started

### 1️⃣ Install dependencies

From the **repository root**:

```bash
uv sync
```

---

### 2️⃣ Set up environment variables

Inside the `project-02-study-buddy` folder:

1. Copy the example file:

   ```bash
   cp .env.example .env
   ```

2. Open `.env` and add your OpenAI API key:

   ```
   OPENAI_API_KEY=your_openai_api_key_here
   ```

⚠️ Never commit `.env` — it is ignored by Git.

---

### 3️⃣ Run the Study Buddy

From inside `project-02-study-buddy`:

```bash
python main.py
```

On first run, it will ask a few questions and save your profile to:

`project-02-study-buddy/memory/user_profile.json`

Next time you run it, it will remember you automatically.

---

## 💬 Example Prompts

Try asking:

* `Explain Python functions like I’m a beginner`
* `Quiz me on what I learned yesterday`
* `Give me a 20-minute study plan for today`
* `Explain this concept with a real-life analogy`

---

## 📌 Key Takeaways

* “Memory” can be simple: **a local file + saved context**
* A personalized agent feels smarter even with the same model
* You still don’t need a UI to build something useful
* Small steps = real progress

---

Built by **Genesis**
Beginner AI Projects Series ✨

---
