"""
Console tool-calling agent that prints its reasoning chain:
    Thought -> Action -> Observation -> ... -> Final Answer

    python -m task3_agent.agent "Read sales.txt, total the revenue, and tell me the average per month"
    python -m task3_agent.agent            # interactive
"""
from __future__ import annotations

import sys

from langchain_core.messages import AIMessage, HumanMessage, SystemMessage, ToolMessage

from common.models import get_chat_model
from task3_agent.tools import TOOLS, TOOLS_BY_NAME

SYSTEM = (
    "You are a research agent with tools: web_search (current facts), calculator (all arithmetic), "
    "read_local_file (files in the workspace). Rules:\n"
    "- Before EVERY tool call, write one short sentence explaining your reasoning.\n"
    "- Never do arithmetic in your head; use the calculator.\n"
    "- Never guess facts that need current information; use web_search.\n"
    "- When you have enough information, give a clear final answer."
)


def _text(msg: AIMessage) -> str:
    c = msg.content
    if isinstance(c, str):
        return c.strip()
    return "".join(b.get("text", "") if isinstance(b, dict) else str(b) for b in c).strip()


def run_agent(question: str, max_steps: int = 8, verbose: bool = True) -> str:
    llm = get_chat_model().bind_tools(TOOLS)
    messages = [SystemMessage(SYSTEM), HumanMessage(question)]

    for step in range(1, max_steps + 1):
        ai: AIMessage = llm.invoke(messages)
        messages.append(ai)
        thought = _text(ai)

        if not ai.tool_calls:
            if verbose:
                print(f"\n=== Final Answer ===\n{thought}\n")
            return thought

        if verbose and thought:
            print(f"\n[Step {step}] Thought: {thought}")
        for call in ai.tool_calls:
            if verbose:
                print(f"[Step {step}] Action: {call['name']}({call['args']})")
            try:
                obs = str(TOOLS_BY_NAME[call["name"]].invoke(call["args"]))
            except Exception as e:
                obs = f"Tool error: {e}"
            if verbose:
                print(f"[Step {step}] Observation: {obs[:500]}{'...' if len(obs) > 500 else ''}")
            messages.append(ToolMessage(content=obs, tool_call_id=call["id"]))

    msg = "I reached the step limit before finishing. Try a more specific question."
    print(f"\n{msg}")
    return msg


def main() -> None:
    if len(sys.argv) > 1:
        run_agent(" ".join(sys.argv[1:]))
        return
    print("Research agent ready (type 'exit' to quit).")
    while (q := input("\nYou: ").strip()).lower() not in {"exit", "quit"}:
        if q:
            run_agent(q)


if __name__ == "__main__":
    main()
