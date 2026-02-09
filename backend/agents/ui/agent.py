"""UI Agent - Chat assistant for vacation planning"""

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, Any, Optional, List

from agents.base import get_llm
from .tools import (
    search_vacation,
    show_package_details,
    start_booking_flow,
    add_to_favorites_action,
    navigate_to_page,
    show_recommendations
)
from agents.database.tools import (
    search_packages,
    get_package_details,
    get_destinations
)

# System prompt for the UI agent
SYSTEM_PROMPT = """Tu es l'assistant VacanceAI, un conseiller vacances expert et amical.

PERSONNALITE:
- Enthousiaste pour les voyages et les découvertes
- Chaleureux et professionnel
- Patient et à l'écoute
- Expert en destinations et packages vacances

TES CAPACITES:
1. Aider à trouver le package vacances idéal selon les envies et le budget
2. Expliquer les détails des offres (ce qui est inclus, durée, prix)
3. Guider dans le processus de réservation
4. Donner des recommandations personnalisées
5. Répondre aux questions sur les destinations

COMPORTEMENT:
- Pose des questions pour comprendre les préférences (destination, budget, durée, type de vacances)
- Propose 2-3 options adaptées avec enthousiasme
- Explique clairement ce qui est inclus dans chaque package
- Utilise les tools pour effectuer des actions sur l'interface
- Si l'utilisateur hésite, propose des alternatives ou des compromis

REPONSES:
- Sois concis mais informatif
- Utilise des emojis avec parcimonie pour rendre la conversation agréable
- Formate les prix et détails de manière claire
- Termine par une question ou une proposition d'action

PACKAGES DISPONIBLES:
- Maldives (plage, luxe, romantique)
- Alpes Suisses (montagne, ski, randonnée)
- Tokyo (ville, culture, gastronomie)
- Kenya (safari, aventure, nature)
- Santorin (plage, romantique, culture)
- Bali (plage, culture, spa)
- New York (ville, culture, shopping)
- Marrakech (culture, gastronomie, aventure)
"""

# Create the UI agent
llm = get_llm(temperature=0.8)

ui_tools = [
    # UI Actions
    search_vacation,
    show_package_details,
    start_booking_flow,
    add_to_favorites_action,
    navigate_to_page,
    show_recommendations,
    # Database access
    search_packages,
    get_package_details,
    get_destinations
]

ui_agent = create_react_agent(
    llm,
    tools=ui_tools,
    prompt=SYSTEM_PROMPT
)


async def invoke_ui_agent(
    message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Invoke the UI agent with a message and conversation context.

    Args:
        message: The user's message
        conversation_history: Previous messages in the conversation
        user_context: User information (id, name, preferences, etc.)

    Returns:
        Agent response with message and any UI actions
    """
    # Build messages
    messages = []

    # Add conversation history
    if conversation_history:
        for msg in conversation_history[-10:]:  # Keep last 10 messages
            if msg["role"] == "user":
                messages.append(HumanMessage(content=msg["content"]))
            else:
                messages.append(AIMessage(content=msg["content"]))

    # Add user context to current message
    if user_context:
        context_info = f"\n[Contexte utilisateur: {user_context}]"
        messages.append(HumanMessage(content=message + context_info))
    else:
        messages.append(HumanMessage(content=message))

    # Invoke agent
    result = await ui_agent.ainvoke({"messages": messages})

    # Extract response and actions
    last_message = result["messages"][-1]

    # Check for UI actions in tool calls
    ui_actions = []
    for msg in result["messages"]:
        if hasattr(msg, "tool_calls"):
            for tool_call in msg.tool_calls:
                if tool_call.get("name") in [
                    "search_vacation", "show_package_details",
                    "start_booking_flow", "add_to_favorites_action",
                    "navigate_to_page", "show_recommendations"
                ]:
                    ui_actions.append(tool_call)

    return {
        "response": last_message.content,
        "ui_actions": ui_actions,
        "conversation": [
            {
                "role": "assistant" if isinstance(m, AIMessage) else "user",
                "content": m.content
            }
            for m in result["messages"]
            if isinstance(m, (HumanMessage, AIMessage))
        ]
    }
