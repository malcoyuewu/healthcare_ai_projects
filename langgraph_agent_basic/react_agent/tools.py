from __future__ import annotations

import os
from typing import List

from dotenv import load_dotenv
import requests
from langchain_core.tools import tool
from langchain_core.messages import AIMessage, HumanMessage, ToolMessage

# Load environment variables from .env at import time
load_dotenv()


@tool
def get_weather(location: str) -> str:
    """Call to get the weather from a specific location.

    This is just a toy implementation to demonstrate tool-calling.
    """
    lower_loc = location.lower()
    if any(city in lower_loc for city in ["sf", "san francisco"]):
        return "It's sunny in San Francisco, but you better look out if you're a Gemini ."
    return f"I am not sure what the weather is in {location}."


# Export the available tools as a list so other modules can iterate them.
tools: List[object] = [get_weather]


@tool
def local_search(query: str, path: str = ".", max_results: int = 5) -> list:
    """Search project files for the query and return matches.

    This is a simple, fast local search useful for demos that doesn't
    rely on external APIs.
    """
    matches: list = []
    q = query.lower()
    for root, _, files in os.walk(path):
        for fname in files:
            if not fname.endswith((".py", ".md", ".txt", ".rst")):
                continue
            try:
                p = os.path.join(root, fname)
                with open(p, "r", encoding="utf-8", errors="ignore") as fh:
                    for i, line in enumerate(fh, start=1):
                        if q in line.lower():
                            matches.append({"file": p, "line": i, "snippet": line.strip()})
                            if len(matches) >= max_results:
                                return matches
            except Exception:
                continue
    return matches


def _safe_eval_arith(expr: str) -> float:
    """Evaluate a simple arithmetic expression safely using ast parsing."""
    import ast

    allowed_nodes = (
        ast.Expression,
        ast.BinOp,
        ast.UnaryOp,
        ast.Num,
        ast.Constant,
        ast.Add,
        ast.Sub,
        ast.Mult,
        ast.Div,
        ast.Pow,
        ast.Mod,
        ast.USub,
        ast.UAdd,
        ast.FloorDiv,
        ast.LShift,
        ast.RShift,
        ast.BitAnd,
        ast.BitOr,
        ast.BitXor,
    )

    node = ast.parse(expr, mode="eval")

    for n in ast.walk(node):
        if not isinstance(n, allowed_nodes):
            raise ValueError("Unsafe expression")

    return eval(compile(node, filename="<ast>", mode="eval"))


@tool
def calc(expression: str) -> str:
    """Safely evaluate a numeric expression and return the result as a string."""
    try:
        result = _safe_eval_arith(expression)
        return str(result)
    except Exception as e:
        return f"error: {e}"


@tool
def current_time(tz: str = "local") -> str:
    """Return the current time. `tz='utc'` returns UTC time."""
    from datetime import datetime, timezone

    if tz.lower() == "utc":
        return datetime.now(timezone.utc).isoformat()
    return datetime.now().isoformat()


@tool
def random_fact(category: str = "space") -> str:
    """Return a random fact from a small local set of facts for demos."""
    import random

    facts = {
        "space": [
            "A day on Venus is longer than its year.",
            "There are more stars in the universe than grains of sand on Earth.",
            "Neutron stars can spin at hundreds of times per second.",
        ],
        "animals": [
            "Octopuses have three hearts.",
            "Cows have best friends and get stressed when separated.",
        ],
    }
    items = facts.get(category.lower(), sum(facts.values(), []))
    return random.choice(items)


@tool
def web_search(query: str, engine: str = "duckduckgo", max_results: int = 5) -> list:
    """Perform a web search and return top results.

    - `engine='duckduckgo'` uses DuckDuckGo Instant Answer API (free, limited).
    - `engine='google'` uses Google Programmable Search JSON API if
      `GOOGLE_CSE_API_KEY` and `GOOGLE_CSE_ID` are set in the environment.

    Returns a list of dicts: {"title","link","snippet"}.
    """
    engine = (engine or "duckduckgo").lower()
    results = []

    if engine == "google":
        api_key = os.getenv("GOOGLE_CSE_API_KEY")
        cse_id = os.getenv("GOOGLE_CSE_ID")
        if not api_key or not cse_id:
            return [{"error": "GOOGLE_CSE_API_KEY and GOOGLE_CSE_ID not set"}]
        url = "https://www.googleapis.com/customsearch/v1"
        try:
            r = requests.get(url, params={"key": api_key, "cx": cse_id, "q": query, "num": max_results}, timeout=10)
            r.raise_for_status()
            data = r.json()
            for item in data.get("items", [])[:max_results]:
                results.append({
                    "title": item.get("title"),
                    "link": item.get("link"),
                    "snippet": item.get("snippet"),
                })
            return results
        except Exception as e:
            return [{"error": f"google search error: {e}"}]

    # Default: DuckDuckGo Instant Answer API (no API key required)
    try:
        dd_url = "https://api.duckduckgo.com/"
        params = {"q": query, "format": "json", "no_html": 1, "skip_disambig": 1}
        r = requests.get(dd_url, params=params, timeout=8)
        r.raise_for_status()
        data = r.json()

        # Try abstract / related topics
        if data.get("AbstractURL"):
            results.append({"title": data.get("Heading") or query, "link": data.get("AbstractURL"), "snippet": data.get("AbstractText")})

        for t in data.get("RelatedTopics", [])[: max_results * 2]:
            if isinstance(t, dict) and t.get("FirstURL"):
                results.append({"title": t.get("Text"), "link": t.get("FirstURL"), "snippet": t.get("Result") or t.get("Text")})
            if len(results) >= max_results:
                break

        return results[:max_results]
    except Exception as e:
        return [{"error": f"duckduckgo search error: {e}"}]


# Update exported tools list
tools = [get_weather, local_search, calc, current_time, random_fact, web_search]


class MockChatModel:
    """A tiny, local chat model used for testing without network calls.

    It implements `invoke(messages, config)` and `bind_tools(tools)` so it
    can stand in for remote chat models in this project. Responses are
    deterministic and inexpensive (no external API calls).
    """

    def __init__(self, model_name: str = "mock", temperature: float = 0.0):
        self.model_name = model_name
        self.temperature = temperature
        self.tools = {}

    def bind_tools(self, tools_list: List[object]):
        # allow tools to be looked up by name if needed
        try:
            self.tools = {t.name: t for t in tools_list}
        except Exception:
            self.tools = {}
        return self

    def invoke(self, messages, config=None):
        # Find the last human message content (if any)
        last_human = None
        for m in reversed(messages):
            if isinstance(m, HumanMessage):
                last_human = m
                break
        prompt = last_human.content if last_human is not None else ""
        lower = prompt.lower()

        # If the conversation already contains a ToolMessage, use its result to form a final answer
        for m in reversed(messages):
            if isinstance(m, ToolMessage):
                # ToolMessage.content is JSON string in nodes.tool_node — just echo it
                content = getattr(m, "content", "")
                try:
                    import json

                    parsed = json.loads(content)
                except Exception:
                    parsed = content
                return AIMessage(content=f"Final answer using tool output: {parsed}")

        # If the human asked for the weather, return a message that requests a tool call
        if "weather in" in lower or ("weather" in lower and any(city in lower for city in ("sf", "san francisco"))):
            # extract a naive location
            loc = "sf"
            parts = prompt.split()
            for i, p in enumerate(parts):
                if p.lower() == "in" and i + 1 < len(parts):
                    loc = parts[i + 1].strip("?.,")
                    break
            msg = AIMessage(content=f"I will call the get_weather tool for {loc}.")
            # attach tool_calls attribute expected by nodes.should_continue / tool_node
            # LangChain tool invocation expects a mapping of parameter names
            msg.tool_calls = [{"id": "tc1", "name": "get_weather", "args": {"location": loc}}]
            return msg

        # If the conversation already contains a ToolMessage, use its result to form a final answer
        for m in reversed(messages):
            if isinstance(m, ToolMessage):
                # ToolMessage.content is JSON string in nodes.tool_node — just echo it
                content = getattr(m, "content", "")
                try:
                    import json

                    parsed = json.loads(content)
                except Exception:
                    parsed = content
                return AIMessage(content=f"Final answer using tool output: {parsed}")

        # Fallback: simple canned replies
        if "fact about space" in lower or "space" in lower:
            reply = "A fun fact: space is not completely empty — it contains sparse gas, dust, and cosmic rays."
        else:
            reply = f"[mock reply] {prompt}"

        return AIMessage(content=reply)


def get_model_with_tools():
    """Return a chat model used by the project.

    Behavior:
    - If `LLM_BACKEND=ollama` and an Ollama client is available, attempt to use it.
    - Otherwise, return a local `MockChatModel` that does not use paid APIs.

    You can set `LLM_BACKEND=ollama` in your `.env` to try Ollama (requires
    a local Ollama daemon and the appropriate python package).
    """
    backend = os.getenv("LLM_BACKEND", "mock").lower()

    if backend == "ollama":
        # Try to use Ollama via langchain or the ollama client if installed.
        try:
            # Preferred: langchain Ollama integration
            from langchain_ollama.chat_models import Ollama

            model_name = os.getenv("OLLAMA_MODEL", "mistral-7b-instruct")
            temperature = float(os.getenv("OPENAI_TEMP", "0"))
            model = Ollama(model=model_name, temperature=temperature)
            return model.bind_tools(tools)
        except Exception:
            # Ollama not available — fall through to mock
            pass

    # Default: return a mock model suitable for offline testing
    mock = MockChatModel()
    return mock.bind_tools(tools)

# from __future__ import annotations

# import os
# from typing import List

# from langchain_openai import ChatOpenAI
# from langchain_core.tools import tool
# from dotenv import load_dotenv

# load_dotenv()


# @tool
# def get_weather(location: str) -> str:
#     """Call to get the weather from a specific location.

#     This is just a toy implementation to demonstrate tool-calling.
#     """
#     lower_loc = location.lower()
#     if any(city in lower_loc for city in ["sf", "san francisco"]):
#         return "It's sunny in San Francisco, but you better look out if you're a Gemini ."
#     return f"I am not sure what the weather is in {location}."


# # Export the available tools as a list so other modules can iterate them.
# # `get_weather` is already decorated with `@tool`, so it's ready to be used.
# tools: List[object] = [get_weather]


# def get_model_with_tools() -> ChatOpenAI:
#     """Return a Chat model configured for this project.

#     Uses `OPENAI_MODEL` and `OPENAI_TEMP` environment variables if present.
#     """
#     model_name = os.getenv("OPENAI_MODEL", "gpt-4o-mini")
#     try:
#         temperature = float(os.getenv("OPENAI_TEMP", "0"))
#     except ValueError:
#         temperature = 0.0
#     return ChatOpenAI(model=model_name, temperature=temperature)


# __all__ = ["get_weather", "tools", "get_model_with_tools"]