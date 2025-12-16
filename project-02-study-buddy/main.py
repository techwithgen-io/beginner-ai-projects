import os
import json
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional

from dotenv import load_dotenv
from rich.console import Console
from rich.panel import Panel

from langchain_openai import ChatOpenAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

# Load .env from THIS folder (project-02-study-buddy)
load_dotenv(dotenv_path=Path(__file__).parent / ".env")

console = Console()

PROFILE_PATH = Path(__file__).parent / "memory" / "user_profile.json"



# Profile (Memory) Helpers
def load_profile() -> Dict[str, Any]:
    if PROFILE_PATH.exists():
        try:
            return json.loads(PROFILE_PATH.read_text(encoding="utf-8"))
        except Exception:
            return {}
    return {}


def save_profile(profile: Dict[str, Any]) -> None:
    PROFILE_PATH.parent.mkdir(parents=True, exist_ok=True)
    PROFILE_PATH.write_text(json.dumps(profile, indent=2), encoding="utf-8")


def profile_is_complete(profile: Dict[str, Any]) -> bool:
    required = ["name", "learning_goal", "experience_level", "style"]
    return all(profile.get(k) for k in required)


def run_onboarding(existing: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    profile = dict(existing or {})
    console.print(Panel.fit("👋 First-time setup: Let’s personalize your Study Buddy", title="Onboarding"))

    name = input("Your name (ex: Genesis): ").strip() or profile.get("name") or "Friend"
    learning_goal = input("What are you learning right now? (ex: Java, AI agents): ").strip() or profile.get("learning_goal") or "AI"
    experience_level = input("Experience level? (beginner / intermediate / advanced): ").strip().lower() or profile.get("experience_level") or "beginner"

    console.print("\nChoose your learning style (type a number):")
    console.print("  1) Simple + short")
    console.print("  2) Examples-heavy")
    console.print("  3) Step-by-step (like a mentor)")
    console.print("  4) Quiz me (ask questions back)")
    style_choice = input("Style (1-4): ").strip()

    style_map = {
        "1": "simple_short",
        "2": "examples_heavy",
        "3": "step_by_step",
        "4": "quiz_me",
    }
    style = style_map.get(style_choice, profile.get("style") or "examples_heavy")

    profile.update(
        {
            "name": name,
            "learning_goal": learning_goal,
            "experience_level": experience_level,
            "style": style,
            "created_at": profile.get("created_at") or datetime.now().isoformat(timespec="seconds"),
            "last_topic": profile.get("last_topic") or "",
            "stuck_points": profile.get("stuck_points") or [],
            "sessions": profile.get("sessions") or [],
        }
    )

    save_profile(profile)
    console.print(Panel.fit("✅ Profile saved! Type /help anytime.", title="Ready"))
    return profile


def pretty_profile(profile: Dict[str, Any]) -> str:
    stuck = profile.get("stuck_points", [])
    stuck_str = ", ".join(stuck) if stuck else "None"
    return (
        f"Name: {profile.get('name')}\n"
        f"Goal: {profile.get('learning_goal')}\n"
        f"Level: {profile.get('experience_level')}\n"
        f"Style: {profile.get('style')}\n"
        f"Last topic: {profile.get('last_topic') or 'None'}\n"
        f"Stuck points: {stuck_str}\n"
    )



# LLM Prompting
def build_system_prompt(profile: Dict[str, Any]) -> str:
    style = profile.get("style", "examples_heavy")
    style_instructions = {
        "simple_short": "Keep responses short and simple. No jargon unless asked.",
        "examples_heavy": "Use concrete examples and mini demos. Explain like I'm learning.",
        "step_by_step": "Explain step-by-step with clear bullets and tiny checkpoints.",
        "quiz_me": "Teach briefly, then ask me 1-2 questions to check understanding.",
    }.get(style, "Use clear explanations with examples.")

    return f"""
You are a context-aware AI Study Buddy.
Your job is to help the user learn efficiently and kindly.

User profile:
- Name: {profile.get('name')}
- Learning goal: {profile.get('learning_goal')}
- Experience level: {profile.get('experience_level')}
- Last topic: {profile.get('last_topic') or 'None'}
- Stuck points: {', '.join(profile.get('stuck_points', [])) or 'None'}

Teaching style rules:
- {style_instructions}

Behavior:
- If the user asks for code, keep it minimal and explain what each part does.
- If the user seems stuck, suggest a smaller step and a quick practice prompt.
- If the user changes topic, update "last_topic" suggestion at the end in a single line like:
  LAST_TOPIC_SUGGESTION: <topic>
- If the user mentions a struggle (ex: "I don't get X"), suggest adding it to stuck points like:
  STUCK_POINT_SUGGESTION: <thing>
""".strip()


def extract_suggestions(text: str) -> Dict[str, str]:
    """Parse LAST_TOPIC_SUGGESTION and STUCK_POINT_SUGGESTION from the model output."""
    suggestions = {}
    for line in text.splitlines():
        line = line.strip()
        if line.startswith("LAST_TOPIC_SUGGESTION:"):
            suggestions["last_topic"] = line.replace("LAST_TOPIC_SUGGESTION:", "").strip()
        if line.startswith("STUCK_POINT_SUGGESTION:"):
            suggestions["stuck_point"] = line.replace("STUCK_POINT_SUGGESTION:", "").strip()
    return suggestions


def clean_assistant_text(text: str) -> str:
    # Remove suggestion lines from display
    cleaned = []
    for line in text.splitlines():
        if line.strip().startswith(("LAST_TOPIC_SUGGESTION:", "STUCK_POINT_SUGGESTION:")):
            continue
        cleaned.append(line)
    return "\n".join(cleaned).strip()


# Commands
def print_help() -> None:
    console.print(
        Panel.fit(
            "\n".join(
                [
                    "Commands:",
                    "  /help                Show commands",
                    "  /profile             Show what I remember",
                    "  /set goal <text>      Set learning goal",
                    "  /set level <text>     Set experience level",
                    "  /set style <simple|examples|steps|quiz>",
                    "  /add stuck <text>     Add a stuck point",
                    "  /forget              Clear memory (profile)",
                    "  /progress            Show recent session notes",
                    "  quit                 Exit (prints a study recap)",
                ]
            ),
            title="Study Buddy Commands",
        )
    )


def normalize_style(value: str) -> Optional[str]:
    v = value.strip().lower()
    mapping = {
        "simple": "simple_short",
        "short": "simple_short",
        "examples": "examples_heavy",
        "example": "examples_heavy",
        "steps": "step_by_step",
        "step": "step_by_step",
        "mentor": "step_by_step",
        "quiz": "quiz_me",
        "questions": "quiz_me",
    }
    return mapping.get(v)


def cmd_set(profile: Dict[str, Any], args: str) -> Dict[str, Any]:
    parts = args.split(" ", 2)
    if len(parts) < 2:
        console.print("[red]Usage:[/red] /set goal <text> OR /set level <text> OR /set style <simple|examples|steps|quiz>")
        return profile

    key = parts[0].strip().lower()
    value = args[len(key):].strip()

    if key == "goal":
        profile["learning_goal"] = value
        console.print(f"✅ Goal updated: {value}")
    elif key == "level":
        profile["experience_level"] = value.lower()
        console.print(f"✅ Level updated: {value}")
    elif key == "style":
        ns = normalize_style(value)
        if not ns:
            console.print("[red]Style must be:[/red] simple | examples | steps | quiz")
            return profile
        profile["style"] = ns
        console.print(f"✅ Style updated: {ns}")
    else:
        console.print("[red]Unknown setting.[/red] Use goal, level, or style.")
        return profile

    save_profile(profile)
    return profile


def cmd_add_stuck(profile: Dict[str, Any], text: str) -> Dict[str, Any]:
    t = text.strip()
    if not t:
        console.print("[red]Usage:[/red] /add stuck <text>")
        return profile
    stuck = profile.get("stuck_points", [])
    if t not in stuck:
        stuck.append(t)
        profile["stuck_points"] = stuck
        save_profile(profile)
        console.print(f"✅ Added stuck point: {t}")
    else:
        console.print("ℹ️ That stuck point is already saved.")
    return profile


def cmd_forget() -> Dict[str, Any]:
    if PROFILE_PATH.exists():
        PROFILE_PATH.unlink()
    console.print(Panel.fit("🧼 Memory cleared. Restarting onboarding…", title="Forgotten"))
    return run_onboarding({})


def cmd_progress(profile: Dict[str, Any]) -> None:
    sessions = profile.get("sessions", [])
    if not sessions:
        console.print("No progress yet. Study with me and I’ll record recaps 🙂")
        return
    last = sessions[-5:]
    lines = []
    for s in last:
        lines.append(f"- {s.get('date')}: {s.get('summary')}")
    console.print(Panel("\n".join(lines), title="Recent Progress (last 5)"))


# Main Chat Loop
def main() -> None:
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY.\n"
            "Create a .env file inside project-02-study-buddy and add:\n"
            "OPENAI_API_KEY=YOUR_KEY_HERE"
        )

    profile = load_profile()
    if not profile_is_complete(profile):
        profile = run_onboarding(profile)

    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)

    console.print(Panel.fit("📚 Study Buddy is ready! Type /help for commands. Type quit to exit.", title="Project 02"))

    session_messages: List[Any] = []

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() == "quit":
            break

        # Commands
        if user_input.startswith("/"):
            if user_input == "/help":
                print_help()
                continue
            if user_input == "/profile":
                console.print(Panel(pretty_profile(profile), title="Your Profile (Memory)"))
                continue
            if user_input.startswith("/set "):
                profile = cmd_set(profile, user_input.replace("/set ", "", 1))
                continue
            if user_input.startswith("/add stuck "):
                profile = cmd_add_stuck(profile, user_input.replace("/add stuck ", "", 1))
                continue
            if user_input == "/forget":
                profile = cmd_forget()
                session_messages = []
                continue
            if user_input == "/progress":
                cmd_progress(profile)
                continue

            console.print("[red]Unknown command.[/red] Type /help")
            continue

        # Normal chat
        system_prompt = build_system_prompt(profile)
        messages = [SystemMessage(content=system_prompt)] + session_messages + [HumanMessage(content=user_input)]

        response = model.invoke(messages)
        raw_text = response.content if isinstance(response.content, str) else str(response.content)

        suggestions = extract_suggestions(raw_text)
        assistant_text = clean_assistant_text(raw_text)

        console.print(f"\nAssistant:\n{assistant_text}")

        # Update memory suggestions if present
        if suggestions.get("last_topic"):
            profile["last_topic"] = suggestions["last_topic"]
        if suggestions.get("stuck_point"):
            sp = suggestions["stuck_point"]
            if sp:
                stuck = profile.get("stuck_points", [])
                if sp not in stuck:
                    stuck.append(sp)
                    profile["stuck_points"] = stuck

        save_profile(profile)

        # Keep a short session buffer
        session_messages.append(HumanMessage(content=user_input))
        session_messages.append(AIMessage(content=assistant_text))
        session_messages = session_messages[-10:]  # last 5 turns


    # Study recap on exit
    console.print("\n📝 Generating your study recap…")

    recap_prompt = f"""
Make a short study recap for {profile.get('name')}.

Include:
1) What we covered today (2-4 bullets)
2) The next best step (1-2 bullets)
3) One quick practice question

Keep it aligned to:
- Goal: {profile.get('learning_goal')}
- Level: {profile.get('experience_level')}
- Style: {profile.get('style')}
""".strip()

    recap_messages = [
        SystemMessage(content=build_system_prompt(profile)),
        HumanMessage(content=recap_prompt),
    ]
    recap = model.invoke(recap_messages).content

    # Save recap to profile sessions
    session_entry = {
        "date": datetime.now().strftime("%Y-%m-%d"),
        "summary": (recap[:180] + "…") if isinstance(recap, str) and len(recap) > 180 else recap,
    }
    sessions = profile.get("sessions", [])
    sessions.append(session_entry)
    profile["sessions"] = sessions
    save_profile(profile)

    console.print(Panel(str(recap), title="✅ Study Recap"))


if __name__ == "__main__":
    main()
