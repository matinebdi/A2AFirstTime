"""Conversation routes - WebSocket chat with UI Agent (Oracle)"""

from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
import json
import uuid

from database.oracle_client import execute_query_single, execute_insert, execute_update
from database.queries import (
    CONVERSATION_BY_ID, CONVERSATION_INSERT, CONVERSATION_UPDATE_MESSAGES,
    CONVERSATION_CLEAR, format_conversation, to_json_string
)
from agents.orchestrator.agent import process_request
from auth.middleware import get_current_user, get_optional_user

router = APIRouter()


class ChatMessage(BaseModel):
    message: str
    context: Optional[Dict[str, Any]] = None


class ConversationResponse(BaseModel):
    response: str
    ui_actions: List[Dict] = []
    conversation_id: str


# Active WebSocket connections
active_connections: Dict[str, WebSocket] = {}


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat with the vacation assistant."""
    await websocket.accept()
    active_connections[conversation_id] = websocket

    # Get or create conversation
    conv_row = execute_query_single(CONVERSATION_BY_ID, {"id": conversation_id})

    history = []
    if conv_row:
        conv = format_conversation(conv_row)
        history = conv.get("messages", [])

    try:
        while True:
            data = await websocket.receive_text()

            try:
                message_data = json.loads(data)
            except json.JSONDecodeError:
                await websocket.send_text(json.dumps({
                    "error": "Invalid JSON",
                    "response": "Message invalide reçu."
                }))
                continue

            user_message = message_data.get("message", "")
            user_context = message_data.get("context", {})

            history.append({
                "role": "user",
                "content": user_message,
                "timestamp": datetime.utcnow().isoformat()
            })

            result = await process_request(
                message=user_message,
                context={
                    "history": history,
                    "user": user_context.get("user"),
                    "conversation_id": conversation_id,
                    **user_context
                }
            )

            history.append({
                "role": "assistant",
                "content": result["response"],
                "timestamp": datetime.utcnow().isoformat(),
                "ui_actions": result.get("ui_actions", [])
            })

            # Save conversation
            messages_json = to_json_string(history)
            if conv_row:
                execute_update(CONVERSATION_UPDATE_MESSAGES, {
                    "messages": messages_json,
                    "id": conversation_id
                })
            else:
                execute_insert(CONVERSATION_INSERT, {
                    "id": conversation_id,
                    "user_id": None,
                    "messages": messages_json,
                    "context": "{}"
                })
                conv_row = True  # Mark as existing for subsequent messages

            await websocket.send_text(json.dumps({
                "response": result["response"],
                "ui_actions": result.get("ui_actions", []),
                "agent_type": result.get("agent_type"),
                "timestamp": datetime.utcnow().isoformat()
            }))

    except WebSocketDisconnect:
        active_connections.pop(conversation_id, None)
    except Exception as e:
        try:
            await websocket.send_text(json.dumps({
                "error": str(e),
                "response": "Une erreur s'est produite. Veuillez réessayer."
            }))
        except Exception:
            pass
        active_connections.pop(conversation_id, None)
        try:
            await websocket.close()
        except Exception:
            pass


@router.post("/{conversation_id}/message")
async def send_message(
    conversation_id: str,
    chat: ChatMessage
) -> ConversationResponse:
    """Send a message to the vacation assistant (REST alternative to WebSocket)."""
    conv_row = execute_query_single(CONVERSATION_BY_ID, {"id": conversation_id})

    history = []
    if conv_row:
        conv = format_conversation(conv_row)
        history = conv.get("messages", [])

    history.append({
        "role": "user",
        "content": chat.message,
        "timestamp": datetime.utcnow().isoformat()
    })

    result = await process_request(
        message=chat.message,
        context={
            "history": history,
            "conversation_id": conversation_id,
            **(chat.context or {})
        }
    )

    history.append({
        "role": "assistant",
        "content": result["response"],
        "timestamp": datetime.utcnow().isoformat(),
        "ui_actions": result.get("ui_actions", [])
    })

    messages_json = to_json_string(history)
    if conv_row:
        execute_update(CONVERSATION_UPDATE_MESSAGES, {
            "messages": messages_json,
            "id": conversation_id
        })
    else:
        execute_insert(CONVERSATION_INSERT, {
            "id": conversation_id,
            "user_id": None,
            "messages": messages_json,
            "context": "{}"
        })

    return ConversationResponse(
        response=result["response"],
        ui_actions=result.get("ui_actions", []),
        conversation_id=conversation_id
    )


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str):
    """Get conversation history."""
    row = execute_query_single(CONVERSATION_BY_ID, {"id": conversation_id})

    if not row:
        return {"messages": [], "conversation_id": conversation_id}

    return format_conversation(row)


@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: str):
    """Clear conversation history."""
    execute_update(CONVERSATION_CLEAR, {"id": conversation_id})
    return {"message": "Conversation cleared"}


@router.post("/new")
async def create_conversation(user=Depends(get_optional_user)):
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())

    execute_insert(CONVERSATION_INSERT, {
        "id": conversation_id,
        "user_id": user.id if user else None,
        "messages": "[]",
        "context": "{}"
    })

    return {"conversation_id": conversation_id}
