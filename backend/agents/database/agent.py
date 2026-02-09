"""Database Agent - LangGraph agent for database operations"""

from langgraph.prebuilt import create_react_agent
from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
from typing import Dict, Any, Optional

from agents.base import get_llm
from .tools import (
    search_packages,
    get_package_details,
    get_destinations,
    create_booking,
    get_user_bookings,
    add_to_favorites,
    get_user_favorites,
    remove_from_favorites
)

# System prompt for the database agent
SYSTEM_PROMPT = """Tu es l'agent de base de données de VacanceAI.

Tu gères toutes les opérations de données pour les packages vacances:
- Rechercher des packages selon les critères (prix, durée, destination, type)
- Récupérer les détails complets d'un package
- Lister les destinations disponibles
- Créer des réservations
- Gérer les favoris des utilisateurs

Instructions:
1. Utilise les outils disponibles pour répondre aux demandes
2. Pour les recherches, utilise les bons filtres selon la demande
3. Retourne toujours des résultats formatés et pertinents
4. Si aucun résultat, suggère des alternatives

Rappel des tags disponibles: beach, mountain, city, adventure, romantic, family, luxury, culture, gastronomy, spa, ski, nature
"""

# Create the database agent
llm = get_llm()

database_tools = [
    search_packages,
    get_package_details,
    get_destinations,
    create_booking,
    get_user_bookings,
    add_to_favorites,
    get_user_favorites,
    remove_from_favorites
]

database_agent = create_react_agent(
    llm,
    tools=database_tools,
    prompt=SYSTEM_PROMPT
)


async def invoke_database_agent(
    message: str,
    context: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Invoke the database agent with a message.

    Args:
        message: The user's request
        context: Optional context (user_id, etc.)

    Returns:
        Agent response with results
    """
    # Prepare input
    messages = [HumanMessage(content=message)]

    if context:
        # Add context to the message
        context_str = f"\nContext: {context}"
        messages[0] = HumanMessage(content=message + context_str)

    # Invoke agent
    result = await database_agent.ainvoke({"messages": messages})

    # Extract response
    last_message = result["messages"][-1]

    return {
        "response": last_message.content,
        "messages": [
            {
                "role": "assistant" if isinstance(m, AIMessage) else "user",
                "content": m.content
            }
            for m in result["messages"]
        ]
    }
