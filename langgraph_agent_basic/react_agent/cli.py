from __future__ import annotations

from .graph_builder import create_graph
from .tools import web_search


def try_web_search_demo():
    """Run a quick web_search demo and print the results."""
    print("Running web_search demo (DuckDuckGo)...")
    res = web_search("alan turing", engine="duckduckgo", max_results=5)
    print("Results:")
    for i, r in enumerate(res, start=1):
        if isinstance(r, dict) and "error" in r:
            print(f" {i}. ERROR: {r['error']}")
            continue
        title = r.get("title") or r.get("snippet") or "(no title)"
        link = r.get("link") or ""
        snippet = r.get("snippet") or ""
        print(f" {i}. {title}\n    {link}\n    {snippet}\n")


def print_stream(stream):
    """Pretty-print messages from a LangGraph stream."""
    for s in stream:
        message = s["messages"][-1]
        # When using tuples for initial user messages, just print them directly
        if isinstance(message, tuple):
            print(message)
        else:
            # LangChain messages usually have pretty_print()
            pretty = getattr(message, "pretty_print", None)
            if callable(pretty):
                pretty()
            else:
                print(message)


def run_example():
    """Run a simple demo query."""
    graph = create_graph()
    inputs = {"messages": [("user", "what is the weather in sf?")]} 
    print_stream(graph.stream(inputs, stream_mode="values"))


def run_simulate_tool():
    """Run the graph with a prompt that triggers the mock model to emit a tool call."""
    graph = create_graph()
    inputs = {"messages": [("user", "what is the weather in sf?")]} 
    print("--- Running simulated tool-call demo ---")
    print_stream(graph.stream(inputs, stream_mode="values"))
    # Also test the web_search tool directly (DuckDuckGo)
    print("--- Running web_search demo (direct tool call) ---")
    try:
        from .tools import web_search

        # web_search may be a StructuredTool (decorated with @tool) or a plain function.
        params = {"query": "alan turing", "engine": "duckduckgo", "max_results": 10}
        if callable(web_search):
            try:
                results = web_search(**params)
            except TypeError:
                # Some tool wrappers accept a single positional arg dict via invoke/run
                if hasattr(web_search, "invoke"):
                    results = web_search.invoke(params)
                elif hasattr(web_search, "run"):
                    results = web_search.run(params)
                else:
                    raise
        elif hasattr(web_search, "invoke"):
            results = web_search.invoke(params)
        elif hasattr(web_search, "run"):
            results = web_search.run(params)
        else:
            raise RuntimeError("web_search tool is not callable and has no invoke/run method")
        if not results:
            print("No results returned from web_search")
        else:
            for i, r in enumerate(results, start=1):
                if isinstance(r, dict) and "error" in r:
                    print(f" {i}. ERROR: {r['error']}")
                    continue
                title = r.get("title") or r.get("snippet") or "(no title)"
                link = r.get("link") or ""
                snippet = r.get("snippet") or ""
                print(f" {i}. {title}\n    {link}\n    {snippet}\n")
    except Exception as e:
        print(f"web_search demo failed: {e}")


def main():
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--web", action="store_true", help="Run web_search demo")
    parser.add_argument("--simulate-tool", action="store_true", help="Run simulated tool-call demo (mock LLM)")
    args = parser.parse_args()

    if args.web:
        try_web_search_demo()
        return
    if args.simulate_tool:
        run_simulate_tool()
        return

    run_example()
    try_web_search_demo()