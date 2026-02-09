"""Google A2A Protocol - Data Models

Based on Google's Agent-to-Agent (A2A) protocol specification.
https://google.github.io/a2a/
"""

from pydantic import BaseModel, Field
from typing import Optional, List, Dict, Any, Literal
from datetime import datetime
from enum import Enum
import uuid


class TaskState(str, Enum):
    """Task execution states"""
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


class MessageRole(str, Enum):
    """Message roles in conversation"""
    USER = "user"
    AGENT = "agent"
    SYSTEM = "system"


class Skill(BaseModel):
    """Agent skill definition"""
    id: str
    name: str
    description: str
    input_schema: Optional[Dict[str, Any]] = None
    output_schema: Optional[Dict[str, Any]] = None


class AgentCapabilities(BaseModel):
    """Agent capabilities"""
    streaming: bool = False
    push_notifications: bool = False
    state_persistence: bool = False


class AgentCard(BaseModel):
    """Agent Card - Metadata describing an agent

    The Agent Card is served at /.well-known/agent.json
    and describes the agent's capabilities and skills.
    """
    name: str
    description: str
    url: str
    version: str = "1.0.0"
    capabilities: AgentCapabilities = Field(default_factory=AgentCapabilities)
    skills: List[Skill] = Field(default_factory=list)
    authentication: Optional[Dict[str, Any]] = None
    metadata: Optional[Dict[str, Any]] = None

    class Config:
        json_schema_extra = {
            "example": {
                "name": "database-agent",
                "description": "Database operations agent for VacanceAI",
                "url": "http://localhost:8000",
                "version": "1.0.0",
                "capabilities": {
                    "streaming": True,
                    "push_notifications": False
                },
                "skills": [
                    {
                        "id": "search_packages",
                        "name": "Search Packages",
                        "description": "Search vacation packages by criteria"
                    }
                ]
            }
        }


class Artifact(BaseModel):
    """Task artifact/output"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    type: str  # "text", "json", "image", "file"
    content: Any
    name: Optional[str] = None
    mime_type: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class Message(BaseModel):
    """Message in task conversation"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    role: MessageRole
    content: str
    artifacts: List[Artifact] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)


class TaskInput(BaseModel):
    """Task input/request"""
    skill_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None
    artifacts: List[Artifact] = Field(default_factory=list)


class TaskOutput(BaseModel):
    """Task output/response"""
    message: str
    artifacts: List[Artifact] = Field(default_factory=list)
    metadata: Optional[Dict[str, Any]] = None


class Task(BaseModel):
    """A2A Task - Unit of work between agents"""
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    state: TaskState = TaskState.PENDING
    input: TaskInput
    output: Optional[TaskOutput] = None
    messages: List[Message] = Field(default_factory=list)
    error: Optional[str] = None
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)
    completed_at: Optional[datetime] = None
    metadata: Optional[Dict[str, Any]] = None

    def start(self):
        """Mark task as running"""
        self.state = TaskState.RUNNING
        self.updated_at = datetime.utcnow()

    def complete(self, output: TaskOutput):
        """Mark task as completed"""
        self.state = TaskState.COMPLETED
        self.output = output
        self.updated_at = datetime.utcnow()
        self.completed_at = datetime.utcnow()

    def fail(self, error: str):
        """Mark task as failed"""
        self.state = TaskState.FAILED
        self.error = error
        self.updated_at = datetime.utcnow()

    def cancel(self):
        """Mark task as cancelled"""
        self.state = TaskState.CANCELLED
        self.updated_at = datetime.utcnow()

    def add_message(self, role: MessageRole, content: str, artifacts: List[Artifact] = None):
        """Add a message to the task conversation"""
        message = Message(
            role=role,
            content=content,
            artifacts=artifacts or []
        )
        self.messages.append(message)
        self.updated_at = datetime.utcnow()
        return message


class TaskCreateRequest(BaseModel):
    """Request to create a new task"""
    skill_id: Optional[str] = None
    message: str
    context: Optional[Dict[str, Any]] = None


class TaskStatusResponse(BaseModel):
    """Task status response"""
    id: str
    state: TaskState
    output: Optional[TaskOutput] = None
    error: Optional[str] = None
    created_at: datetime
    updated_at: datetime
    completed_at: Optional[datetime] = None
