"""Conversation routes - WebSocket chat with UI Agent (Oracle)"""

import json
import uuid
from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException, Depends
from pydantic import BaseModel
from typing import Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session

from database.session import get_db, create_session
from database.models import Conversation
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


def _to_json(value):
    """Convert a Python object to a JSON string for CLOB storage."""
    if value is None:
        return None
    if isinstance(value, str):
        return value
    return json.dumps(value, ensure_ascii=False)


@router.websocket("/ws/{conversation_id}")
async def websocket_chat(websocket: WebSocket, conversation_id: str):
    """WebSocket endpoint for real-time chat with the vacation assistant."""
    await websocket.accept()
    active_connections[conversation_id] = websocket

    # Get or create conversation (manual session for WebSocket)
    db = create_session()
    try:
        conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
        history = []
        if conv:
            history = conv.messages or []
        conv_exists = conv is not None
    finally:
        db.close()

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

            # Save conversation (new session per message)
            db = create_session()
            try:
                messages_json = _to_json(history)
                if conv_exists:
                    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
                    if conv:
                        conv.messages = messages_json
                        db.commit()
                else:
                    new_conv = Conversation(
                        id=conversation_id,
                        user_id=None,
                        messages=messages_json,
                        context="{}",
                    )
                    db.add(new_conv)
                    db.commit()
                    conv_exists = True
            finally:
                db.close()

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
    chat: ChatMessage,
    db: Session = Depends(get_db),
) -> ConversationResponse:
    """Send a message to the vacation assistant (REST alternative to WebSocket)."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    history = []
    if conv:
        history = conv.messages or []

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

    messages_json = _to_json(history)
    if conv:
        conv.messages = messages_json
    else:
        new_conv = Conversation(
            id=conversation_id,
            user_id=None,
            messages=messages_json,
            context="{}",
        )
        db.add(new_conv)
    db.commit()

    return ConversationResponse(
        response=result["response"],
        ui_actions=result.get("ui_actions", []),
        conversation_id=conversation_id
    )


@router.get("/{conversation_id}")
async def get_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Get conversation history."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()

    if not conv:
        return {"messages": [], "conversation_id": conversation_id}

    return conv.to_dict()


@router.delete("/{conversation_id}")
async def clear_conversation(conversation_id: str, db: Session = Depends(get_db)):
    """Clear conversation history."""
    conv = db.query(Conversation).filter(Conversation.id == conversation_id).first()
    if conv:
        conv.messages = "[]"
        db.commit()
    return {"message": "Conversation cleared"}


@router.post("/new")
async def create_conversation(
    user=Depends(get_optional_user),
    db: Session = Depends(get_db),
):
    """Create a new conversation."""
    conversation_id = str(uuid.uuid4())

    conv = Conversation(
        id=conversation_id,
        user_id=user.id if user else None,
        messages="[]",
        context="{}",
    )
    db.add(conv)
    db.commit()

    return {"conversation_id": conversation_id}
