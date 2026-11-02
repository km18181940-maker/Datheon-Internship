"""Agent tools: web search, math calculator, sandboxed local file reader."""
import os
from pathlib import Path

from langchain_core.tools import tool

from common.safety import resolve_in_workspace, safe_eval

WORKSPACE = Path(os.getenv("AGENT_WORKSPACE", Path(__file__).parent / "workspace"))
MAX_FILE_CHARS = 6000


@tool
def web_search(query: str) -> str:
    """Search the web with DuckDuckGo for current facts. Returns the top results (title, URL, snippet)."""
    try:
        from ddgs import DDGS

        results = DDGS().text(query, max_results=5)
    except Exception as e:  # network / rate limit: let the agent see and adapt
        return f"Search failed: {e}"
    if not results:
        return "No results found."
    return "\n\n".join(f"{r.get('title')}\n{r.get('href')}\n{r.get('body')}" for r in results)


@tool
def calculator(expression: str) -> str:
    """Evaluate a math expression, e.g. '(120*1.08)/3' or 'sqrt(144)+2**5'. Supports + - * / // % ** and sqrt/log/sin/cos/min/max/round."""
    try:
        return str(safe_eval(expression))
    except Exception as e:
        return f"Calculator error: {e}"


@tool
def read_local_file(path: str) -> str:
    """Read a text file from the agent workspace folder (relative path, e.g. 'sales.txt'). Use '.' to list available files."""
    try:
        target = resolve_in_workspace(WORKSPACE, path)
        if target.is_dir():
            return "Files: " + ", ".join(sorted(p.name for p in target.iterdir()))
        text = target.read_text(encoding="utf-8", errors="replace")
        return text[:MAX_FILE_CHARS] + ("\n...[truncated]" if len(text) > MAX_FILE_CHARS else "")
    except Exception as e:
        return f"File error: {e}"


TOOLS = [web_search, calculator, read_local_file]
TOOLS_BY_NAME = {t.name: t for t in TOOLS}
