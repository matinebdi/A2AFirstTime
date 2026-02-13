"""Graph exports for LangGraph Studio (without custom checkpointers).

LangGraph API handles persistence internally, so custom checkpointers
are not allowed. This module re-creates the agents without them.
"""

from langgraph.prebuilt import create_react_agent

from agents.base import get_llm
from agents.orchestrator.agent import orchestrator_agent
from agents.ui.agent import ui_tools, SYSTEM_PROMPT as UI_PROMPT
from agents.database.agent import database_tools, SYSTEM_PROMPT as DB_PROMPT

# UI agent (no custom checkpointer - LangGraph API handles persistence)
ui_agent = create_react_agent(
    get_llm(temperature=0.8),
    tools=ui_tools,
    prompt=UI_PROMPT,
)

# Database agent
database_agent = create_react_agent(
    get_llm(),
    tools=database_tools,
    prompt=DB_PROMPT,
)
