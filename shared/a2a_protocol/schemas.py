"""A2A Protocol Message Schemas"""

from datetime import datetime
from enum import Enum
from typing import Any, Optional
from uuid import uuid4

from pydantic import BaseModel, Field


class MessageType(str, Enum):
    """Types of A2A messages"""
    REQUEST = "request"
    RESPONSE = "response"
    EVENT = "event"


class Priority(str, Enum):
    """Message priority levels"""
    HIGH = "high"
    NORMAL = "normal"
    LOW = "low"


class A2AMessage(BaseModel):
    """
    Agent-to-Agent Protocol Message

    This is the standard message format for communication between agents.
    All agents must send and receive messages in this format.
    """
    message_id: str = Field(default_factory=lambda: str(uuid4()))
    from_agent: str = Field(..., description="Name of the sending agent")
    to_agent: str = Field(..., description="Name of the receiving agent")
    message_type: MessageType = Field(..., description="Type of message")
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    payload: dict[str, Any] = Field(..., description="Message payload/data")
    callback_id: Optional[str] = Field(None, description="ID of the message this responds to")
    correlation_id: Optional[str] = Field(None, description="Workflow correlation ID")
    priority: Priority = Field(default=Priority.NORMAL)

    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

    def to_dict(self) -> dict:
        """Convert message to dictionary"""
        return self.model_dump(mode='json')

    @classmethod
    def from_dict(cls, data: dict) -> "A2AMessage":
        """Create message from dictionary"""
        return cls(**data)
