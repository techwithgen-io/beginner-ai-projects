import os
from dotenv import load_dotenv

from langchain_core.messages import HumanMessage
from langchain_openai import ChatOpenAI
from langchain.tools import tool
from langgraph.prebuilt import create_react_agent

# Load environment variables from .env
load_dotenv()


@tool
def calculator(a: float, b: float) -> str:
    """Add two numbers."""
    return f"The sum of {a} and {b} is {a + b}"


@tool
def say_hello(name: str) -> str:
    """Greet a user by name."""
    return f"Hello {name}, I hope you are well today."


def run_chat() -> None:
    # Ensure API key is present
    if not os.getenv("OPENAI_API_KEY"):
        raise RuntimeError(
            "Missing OPENAI_API_KEY. Add it to your .env file as:\n"
            "OPENAI_API_KEY=sk-..."
        )

    # Create model + agent
    model = ChatOpenAI(model="gpt-4o-mini", temperature=0)
    tools = [calculator, say_hello]
    agent = create_react_agent(model, tools)

    print("Welcome! I'm your AI assistant. Type 'quit' to exit.")
    print("Try: 'hi im genesis' or '5 + 5' or 'say hello to Genesis'")

    while True:
        user_input = input("\nYou: ").strip()

        if user_input.lower() in {"quit", "exit"}:
            print("Bye! 👋")
            break

        # Output 
        result = agent.invoke({"messages": [HumanMessage(content=user_input)]})
        assistant_text = result["messages"][-1].content

        print("\nAssistant:", assistant_text)


if __name__ == "__main__":
    run_chat()
