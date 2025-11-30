from __future__ import annotations

import json
from typing import Dict

from langchain_core.messages import ToolMessage, SystemMessage
from langchain_core.runnables import RunnableConfig

from .state import AgentState
from .tools import tools, get_model_with_tools


# Bind tools once at module import
model = get_model_with_tools()
tools_by_name: Dict[str, object] = {tool.name: tool for tool in tools}


def tool_node(state: AgentState) -> dict:
    """Node that executes requested tools and returns their outputs as messages."""
    outputs = []
    last_message = state["messages"][-1]
    for tool_call in getattr(last_message, "tool_calls", []):
        tool_name = tool_call["name"]
        tool_args = tool_call["args"]
        tool = tools_by_name[tool_name]
        tool_result = tool.invoke(tool_args)
        outputs.append(
            ToolMessage(
                content=json.dumps(tool_result),
                name=tool_name,
                tool_call_id=tool_call["id"],
            )
        )
    return {"messages": outputs}


def call_model(state: AgentState, config: RunnableConfig | None = None) -> dict:
    """Node that calls the LLM with a system prompt + conversation history."""
    if config is None:
        config = RunnableConfig()

    system_prompt = SystemMessage(
        "You are a helpful AI assistant, please respond to the user's query to the best of your ability!"
    )
    # state["messages"] is a sequence; convert to list to be safe
    history = list(state["messages"])
    try:
        response = model.invoke([system_prompt] + history, config)
    except Exception as e:
        # Convert runtime errors (rate limits, auth, etc.) into a SystemMessage
        return {
            "messages": [
                SystemMessage(
                    content=(
                        "Error calling language model: "
                        + (str(e) or "unknown error")
                    )
                )
            ]
        }
    return {"messages": [response]}


def should_continue(state: AgentState) -> str:
    """Decide whether to continue (call tools) or end.

    - If the last AI message has tool calls -> return "continue"
    - Otherwise -> return "end"
    """
    messages = state["messages"]
    last_message = messages[-1]
    # If there is no function/tool call, then we finish
    if not getattr(last_message, "tool_calls", None):
        return "end"
    # Otherwise, we continue to the tool node
    return "continue"