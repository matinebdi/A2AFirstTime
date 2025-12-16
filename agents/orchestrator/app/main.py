"""Orchestrator Agent - Main FastAPI Application"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

# Import from shared protocol
import sys
sys.path.append("/app")
from shared.a2a_protocol import A2AMessage, MessageType, Priority, A2AClient

from .config import settings

# Configure logging
logging.basicConfig(
    level=getattr(logging, settings.log_level),
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger(__name__)

# Global A2A client
a2a_client: A2AClient = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global a2a_client

    # Startup
    logger.info("🚀 Starting Orchestrator Agent...")
    a2a_client = A2AClient(
        agent_name=settings.agent_name,
        redis_host=settings.redis_host,
        redis_port=settings.redis_port,
        redis_password=settings.redis_password,
        redis_db=settings.redis_db,
        channel_prefix=settings.a2a_channel_prefix
    )

    try:
        await a2a_client.connect()

        # Register message handlers
        a2a_client.register_handler("test", handle_test_message)
        a2a_client.register_handler("decision_response", handle_decision_response)

        # Start listening in background
        asyncio.create_task(a2a_client.listen())

        logger.info("✅ Orchestrator Agent is ready!")

    except Exception as e:
        logger.error(f"❌ Failed to start Orchestrator: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Orchestrator Agent...")
    if a2a_client:
        await a2a_client.disconnect()


app = FastAPI(
    title="Orchestrator Agent",
    description="Main coordinator for A2A multi-agent system",
    version="1.0.0",
    lifespan=lifespan,
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# === Request Models ===


class TaskRequest(BaseModel):
    """Request to execute a task"""
    task: str
    context: dict = {}
    priority: str = "normal"


class AgentMessageRequest(BaseModel):
    """Request to send a message to an agent"""
    to_agent: str
    task: str
    context: dict = {}
    priority: str = "normal"


# === Message Handlers ===


async def handle_test_message(message: A2AMessage):
    """Handle test messages"""
    logger.info(f"Received test message: {message.payload}")

    # Send response back
    await a2a_client.send_message(
        to_agent=message.from_agent,
        payload={"result": "Test received!", "original_payload": message.payload},
        message_type=MessageType.RESPONSE,
        callback_id=message.message_id,
    )


async def handle_decision_response(message: A2AMessage):
    """Handle response from Decision Agent"""
    logger.info(f"Decision Agent response: {message.payload}")

    # Here you would typically:
    # 1. Process the decision
    # 2. Execute actions based on the decision
    # 3. Forward to other agents if needed
    # 4. Update database/state
    # 5. Send response to frontend via WebSocket


# === API Endpoints ===


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "agent": "orchestrator",
        "status": "running",
        "version": "1.0.0",
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_status = "connected" if a2a_client and a2a_client.redis_client else "disconnected"

    return {
        "status": "healthy",
        "agent": settings.agent_name,
        "redis": redis_status,
        "environment": settings.environment,
    }


@app.post("/execute")
async def execute_task(request: TaskRequest):
    """
    Execute a task by delegating to appropriate agents

    This is the main entry point for task execution.
    The orchestrator will analyze the task and send it to the right agent.
    """
    logger.info(f"Received task: {request.task}")

    try:
        # For now, we'll send all tasks to the decision agent
        # In a production system, you'd have logic to determine which agent to use
        message = await a2a_client.send_message(
            to_agent="decision",
            payload={
                "task": "analyze_and_decide",
                "user_task": request.task,
                "context": request.context,
            },
            message_type=MessageType.REQUEST,
            priority=Priority[request.priority.upper()],
        )

        return {
            "status": "dispatched",
            "message_id": message.message_id,
            "task": request.task,
            "sent_to": "decision",
        }

    except Exception as e:
        logger.error(f"Error executing task: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/send-message")
async def send_message(request: AgentMessageRequest):
    """
    Send a direct message to a specific agent

    This endpoint allows manual testing of agent communication.
    """
    try:
        message = await a2a_client.send_message(
            to_agent=request.to_agent,
            payload={
                "task": request.task,
                "context": request.context,
            },
            message_type=MessageType.REQUEST,
            priority=Priority[request.priority.upper()],
        )

        return {
            "status": "sent",
            "message_id": message.message_id,
            "to_agent": request.to_agent,
        }

    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get orchestrator status and metrics"""
    return {
        "agent": settings.agent_name,
        "environment": settings.environment,
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "a2a_channel_prefix": settings.a2a_channel_prefix,
        "listening": a2a_client._listening if a2a_client else False,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
