from __future__ import annotations

from langgraph.graph import StateGraph, END

from .state import AgentState
from .nodes import call_model, tool_node, should_continue


def create_graph():
    """Create and compile the ReAct LangGraph graph."""
    workflow = StateGraph(AgentState)

    # Define nodes
    workflow.add_node("agent", call_model)
    workflow.add_node("tools", tool_node)

    # Entry point
    workflow.set_entry_point("agent")

    # Conditional edges from agent -> tools or END
    workflow.add_conditional_edges(
        "agent",
        should_continue,
        {
            "continue": "tools",
            "end": END,
        },
    )

    # After tools, go back to agent
    workflow.add_edge("tools", "agent")

    # Compile graph
    graph = workflow.compile()
    return graph