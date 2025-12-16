# Project 01 — CLI AI Agent 🤖

This is **Project 01** in the **Beginner AI Projects** series.

In this project, we build a simple **command-line AI agent** that can understand user input and call tools to perform actions like calculations and greetings.

The goal of this project is to show beginners how AI agents actually work without a UI or unnecessary complexity.

---

## 🧠 What You’ll Learn
- How AI agents work conceptually
- How to use LangChain with a ReAct-style agent
- How to define and call tools
- How to safely manage API keys using `.env`
- How to run an AI project locally

---

## 🛠 Tech Stack
- Python
- LangChain
- LangGraph
- OpenAI API
- `uv` (dependency management)

---

## 📂 Project Structure

```

project-01-ai-agent/
├─ main.py
├─ README.md
├─ pyproject.toml
├─ uv.lock
├─ .env.example

````

---

## 🚀 Getting Started

### 1️⃣ Install dependencies
From the **repository root**:

```bash
uv sync
````

---

### 2️⃣ Set up environment variables

Inside the `project-01-ai-agent` folder:

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

### 3️⃣ Run the agent

From inside `project-01-ai-agent`:

```bash
python main.py
```

---

## 💬 Example Prompts

Try asking:

* `hi im genesis`
* `5 + 5`
* `what can you do?`

---

## 📌 Key Takeaways

* AI agents are loops + tools + models
* Tool calling makes AI useful
* You don’t need a UI to learn AI
* Small projects build real confidence


---

Built by **Genesis**
Beginner AI Projects Series ✨

