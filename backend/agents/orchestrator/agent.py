"""Orchestrator Agent - Routes and coordinates between specialized agents"""

from langgraph.graph import StateGraph, END
from langchain_core.messages import HumanMessage, AIMessage
from typing import TypedDict, Optional, List, Dict, Any, Literal
from enum import Enum
import logging
import traceback

logger = logging.getLogger("agents.orchestrator")

from agents.base import get_llm
from agents.database.agent import invoke_database_agent
from agents.ui.agent import invoke_ui_agent


class AgentType(str, Enum):
    """Types of specialized agents"""
    DATABASE = "database"
    UI = "ui"
    END = "end"


class OrchestratorState(TypedDict):
    """State for the orchestrator workflow"""
    message: str
    skill_id: Optional[str]
    context: Optional[Dict[str, Any]]
    agent_type: Optional[str]
    response: Optional[str]
    ui_actions: List[Dict]
    error: Optional[str]


def classify_request(state: OrchestratorState) -> str:
    """Classify the request and route to appropriate agent.

    Routes based on:
    - skill_id if provided
    - Message content analysis
    """
    skill_id = state.get("skill_id")
    message = state["message"].lower()

    # Route by skill_id
    if skill_id:
        skill_routing = {
            "search_vacations": AgentType.UI,
            "book_package": AgentType.UI,
            "get_recommendations": AgentType.UI,
            "chat_assistant": AgentType.UI,
            "query_database": AgentType.DATABASE,
            "get_data": AgentType.DATABASE
        }
        return skill_routing.get(skill_id, AgentType.UI).value

    # Route by message content
    database_keywords = [
        "query", "database", "sql", "data", "report",
        "statistics", "count", "list all", "export"
    ]

    ui_keywords = [
        "book", "reserve", "search", "find", "show",
        "recommend", "help", "want", "looking for",
        "vacation", "holiday", "trip", "travel",
        "destination", "package", "price", "budget",
        "je cherche", "je veux", "montre", "reserve"
    ]

    # Check for database keywords
    if any(kw in message for kw in database_keywords):
        return AgentType.DATABASE.value

    # Default to UI agent for conversational requests
    if any(kw in message for kw in ui_keywords):
        return AgentType.UI.value

    # Default to UI for general conversation
    return AgentType.UI.value


async def handle_database_agent(state: OrchestratorState) -> OrchestratorState:
    """Process request with database agent"""
    try:
        result = await invoke_database_agent(
            message=state["message"],
            context=state.get("context")
        )
        state["response"] = result["response"]
        state["agent_type"] = AgentType.DATABASE.value
    except Exception as e:
        logger.error(f"Database agent error: {e}\n{traceback.format_exc()}")
        state["error"] = f"Database agent error: {str(e)}"
        state["response"] = "Une erreur s'est produite lors de l'accès aux données."

    return state


async def handle_ui_agent(state: OrchestratorState) -> OrchestratorState:
    """Process request with UI agent"""
    try:
        context = state.get("context") or {}
        result = await invoke_ui_agent(
            message=state["message"],
            conversation_history=context.get("history"),
            user_context=context.get("user"),
            conversation_id=context.get("conversation_id"),
            page_context=context.get("page")
        )
        state["response"] = result["response"]
        state["ui_actions"] = result.get("ui_actions", [])
        state["agent_type"] = AgentType.UI.value
    except Exception as e:
        logger.error(f"UI agent error: {e}\n{traceback.format_exc()}")
        state["error"] = f"UI agent error: {str(e)}"
        state["response"] = "Je rencontre un problème technique. Pouvez-vous reformuler votre demande?"

    return state


def route_to_agent(state: OrchestratorState) -> Literal["database", "ui"]:
    """Route to the appropriate agent based on classification"""
    agent_type = classify_request(state)
    logger.info("Routing request to '%s' agent | message='%s'", agent_type, state["message"][:100])
    return agent_type


# Build the orchestrator graph
workflow = StateGraph(OrchestratorState)


# Add nodes
workflow.add_node("database", handle_database_agent)
workflow.add_node("ui", handle_ui_agent)

# Add conditional routing from start
workflow.add_conditional_edges(
    "__start__",
    route_to_agent,
    {
        "database": "database",
        "ui": "ui"
    }
)

# Add edges to end
workflow.add_edge("database", END)
workflow.add_edge("ui", END)

# Compile the orchestrator
orchestrator_agent = workflow.compile()


async def process_request(
    message: str,
    skill_id: Optional[str] = None,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Process a request through the orchestrator.

    Args:
        message: The user's message
        skill_id: Optional skill to invoke
        context: Optional context (user info, conversation history, etc.)

    Returns:
        Response with message and any UI actions
    """
    initial_state: OrchestratorState = {
        "message": message,
        "skill_id": skill_id,
        "context": context,
        "agent_type": None,
        "response": None,
        "ui_actions": [],
        "error": None
    }

    result = await orchestrator_agent.ainvoke(initial_state)

    return {
        "response": result.get("response", ""),
        "agent_type": result.get("agent_type"),
        "ui_actions": result.get("ui_actions", []),
        "error": result.get("error"),
        "metadata": {
            "skill_id": skill_id,
            "routed_to": result.get("agent_type")
        }
    }
