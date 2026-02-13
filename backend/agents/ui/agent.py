"""UI Agent - Chat assistant for vacation planning"""

from langgraph.prebuilt import create_react_agent
from langgraph.checkpoint.memory import MemorySaver
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage, ToolMessage
from typing import Dict, Any, Optional, List
import json
import logging

logger = logging.getLogger(__name__)

from agents.base import get_llm
from .tools import (
    search_vacation,
    show_package_details,
    start_booking_flow,
    create_booking_action,
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
3. Créer des réservations directement dans la conversation (utilise create_booking_action)
4. Donner des recommandations personnalisées
5. Répondre aux questions sur les destinations

RESERVATION DIRECTE:
- Quand l'utilisateur veut réserver, utilise create_booking_action avec le user_id du contexte utilisateur
- Tu as besoin de: package_id, start_date (YYYY-MM-DD), num_persons
- Si des infos manquent, demande-les avant de réserver
- Si l'utilisateur n'est pas connecté (pas de user_id dans le contexte), dis-lui de se connecter d'abord

COMPORTEMENT:
- Pose des questions pour comprendre les préférences (destination, budget, durée, type de vacances)
- Propose 2-3 options adaptées avec enthousiasme
- Explique clairement ce qui est inclus dans chaque package
- Utilise les tools pour effectuer des actions sur l'interface
- Si l'utilisateur hésite, propose des alternatives ou des compromis

REPONSES:
- Réponds TOUJOURS dans la langue utilisée par l'utilisateur (français si il parle français, anglais si il parle anglais, etc.)
- Sois concis mais informatif
- N'utilise JAMAIS d'emojis dans tes réponses, reste professionnel et textuel
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

CONTEXTE DE PAGE:
- Tu reçois le contexte de la page que l'utilisateur consulte actuellement (page, route, données affichées)
- Utilise-le pour personnaliser tes réponses (ex: si l'utilisateur est sur un package, propose de le réserver)
- Si l'utilisateur dit "celui-ci", "ce package", "celui-la", "le premier", etc., réfère-toi aux données de sa page courante
- Utilise les IDs des packages/bookings du contexte pour appeler les tools (show_package_details, create_booking_action, etc.)
- Exemples:
  - Page packageDetail avec package_id → l'utilisateur parle de ce package
  - Page search avec results → "le premier" = premier résultat affiché
  - Page bookings avec bookings list → "ma dernière réservation" = dernière de la liste
"""

# Create the UI agent
llm = get_llm(temperature=0.8)

ui_tools = [
    # UI Actions
    search_vacation,
    show_package_details,
    start_booking_flow,
    create_booking_action,
    add_to_favorites_action,
    navigate_to_page,
    show_recommendations,
    # Database access
    search_packages,
    get_package_details,
    get_destinations
]

# In-memory checkpointer for conversation state persistence
memory = MemorySaver()

ui_agent = create_react_agent(
    llm,
    tools=ui_tools,
    prompt=SYSTEM_PROMPT,
    checkpointer=memory
)


async def invoke_ui_agent(
    message: str,
    conversation_history: Optional[List[Dict[str, str]]] = None,
    user_context: Optional[Dict[str, Any]] = None,
    conversation_id: Optional[str] = None,
    page_context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Invoke the UI agent with a message and conversation context.

    Args:
        message: The user's message
        conversation_history: Previous messages in the conversation
        user_context: User information (id, name, preferences, etc.)
        conversation_id: Conversation thread ID for checkpointer memory
        page_context: Current page context (page name, route, displayed data)

    Returns:
        Agent response with message and any UI actions
    """
    # Build config with thread_id for checkpointer
    config = None
    use_checkpointer = conversation_id is not None
    if use_checkpointer:
        config = {"configurable": {"thread_id": conversation_id}}
        logger.info(f"UI Agent using checkpointer with thread_id={conversation_id}")

    # Build context suffix
    context_parts = []
    if user_context:
        context_parts.append(f"[Contexte utilisateur: {user_context}]")
    if page_context:
        context_parts.append(f"[Page actuelle: {page_context}]")
    context_suffix = "\n" + "\n".join(context_parts) if context_parts else ""

    # Build messages
    messages = []

    if use_checkpointer:
        # With checkpointer active, only send the new message
        # The checkpointer manages conversation history (including tool calls/results)
        messages.append(HumanMessage(content=message + context_suffix))
    else:
        # Fallback: manually reconstruct history (no checkpointer)
        if conversation_history:
            for msg in conversation_history[-10:]:
                if msg["role"] == "user":
                    messages.append(HumanMessage(content=msg["content"]))
                else:
                    messages.append(AIMessage(content=msg["content"]))

        messages.append(HumanMessage(content=message + context_suffix))

    # Invoke agent
    result = await ui_agent.ainvoke({"messages": messages}, config=config)

    # Extract response and actions
    last_message = result["messages"][-1]

    # Extract UI actions only from the CURRENT turn's ToolMessages
    # (messages after the last HumanMessage to avoid replaying old actions)
    ui_actions = []
    all_msgs = result["messages"]
    last_human_idx = -1
    for i in range(len(all_msgs) - 1, -1, -1):
        if isinstance(all_msgs[i], HumanMessage):
            last_human_idx = i
            break

    for msg in all_msgs[last_human_idx + 1:]:
        if isinstance(msg, ToolMessage):
            try:
                content = msg.content
                if isinstance(content, str):
                    content = json.loads(content)
                if isinstance(content, dict) and "action" in content:
                    ui_actions.append(content)
            except (json.JSONDecodeError, TypeError):
                pass

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
