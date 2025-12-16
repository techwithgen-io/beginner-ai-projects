# Project 02 — Context-Aware AI Study Buddy 🧠📚

A beginner-friendly AI agent that remembers **how you learn**, not just what you say.

This project builds on Project 01 by introducing **persistent memory**.  
Instead of treating every session as a fresh chat, the Study Buddy remembers your learning goals, experience level, and preferences to respond like a personalized tutor.

---

## ✨ What This Project Does

- Remembers your:
  - Name
  - Learning goal (ex: Python, AI agents, Java)
  - Experience level (beginner / intermediate / advanced)
- Adapts explanations based on your preferences
- Saves memory locally between runs
- Provides a friendly CLI study experience

This is **not** just chat history — it’s *learning context*.

---

## 🧠 How Memory Works

The agent stores a lightweight user profile in a local JSON file:

memory/user_profile.json

yaml
Copy code

This file is:
- Created automatically on first run
- Updated as you continue learning
- Loaded on every new session

No database required — perfect for beginners.

---

## 📁 Project Structure

project-02-study-buddy/
├─ main.py # Study Buddy logic
├─ README.md # This file
├─ pyproject.toml
├─ uv.lock
├─ memory/ # Persistent memory (auto-generated)
│ └─ user_profile.json
├─ .env.example # Environment variable template

yaml
Copy code

> ⚠️ `.env` is intentionally NOT committed.

---

## 🚀 Getting Started

### 1️⃣ Set up your environment

From the project folder:

```bash
uv sync
(or install dependencies manually if not using uv)

2️⃣ Add your OpenAI API key
Create a .env file in this folder:

env
Copy code
OPENAI_API_KEY=your_openai_api_key_here
⚠️ Never commit your .env file — it is ignored by Git.

3️⃣ Run the Study Buddy
bash
Copy code
python main.py
On first run, you’ll be guided through a short onboarding to personalize your Study Buddy.

💬 Example Interaction
sql
Copy code
🐣 First-time setup: Let’s personalize your Study Buddy

Your name: Genesis
What are you learning right now?: Python
Experience level?: beginner
Later sessions will automatically remember this context.

🔐 Security Notes
API keys are stored locally in .env

.env.example is provided for reference

No secrets are pushed to GitHub

🧩 What You Learn From This Project
How to add persistent memory to an AI agent

How to structure multi-project repositories

Safe handling of environment variables

Building AI tools that adapt to the user

🔜 What’s Next
This project is part of the Beginner AI Projects series.

Next projects will explore:

Smarter memory strategies

Progress tracking

AI agents with goals and planning

Turning agents into apps

Built by Genesis
Part of the Beginner AI Projects series 💚