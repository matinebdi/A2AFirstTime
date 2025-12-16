"""Decision Agent - AI-powered decision maker using Google Gemini"""

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

from .ai_service import ai_service
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
    logger.info("🚀 Starting Decision Agent...")

    # Initialize AI service
    ai_service.initialize()

    # Initialize A2A client
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
        a2a_client.register_handler("analyze_and_decide", handle_analyze_and_decide)
        a2a_client.register_handler("evaluate_context", handle_evaluate_context)
        a2a_client.register_handler("test", handle_test_message)

        # Start listening in background
        asyncio.create_task(a2a_client.listen())

        logger.info("✅ Decision Agent is ready!")

    except Exception as e:
        logger.error(f"❌ Failed to start Decision Agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Decision Agent...")
    if a2a_client:
        await a2a_client.disconnect()


app = FastAPI(
    title="Decision Agent",
    description="AI-powered decision maker for A2A multi-agent system",
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


class DecisionRequest(BaseModel):
    """Request for AI decision"""
    task: str
    context: dict = {}


class EvaluationRequest(BaseModel):
    """Request for context evaluation"""
    context: dict


# === Message Handlers ===


async def handle_analyze_and_decide(message: A2AMessage):
    """
    Handle analyze_and_decide request from orchestrator

    This is the main decision-making handler that uses Gemini AI
    to analyze tasks and create action plans.
    """
    logger.info(f"Analyzing task: {message.payload.get('user_task', 'unknown')}")

    try:
        user_task = message.payload.get("user_task", "")
        context = message.payload.get("context", {})

        # Use AI to analyze the task
        decision_result = await ai_service.analyze_task(user_task, context)

        # Send response back to orchestrator
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "decision_response",
                "original_task": user_task,
                "decision": decision_result,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
            correlation_id=message.correlation_id,
        )

        logger.info(f"Decision sent: {decision_result.get('decision', 'unknown')}")

    except Exception as e:
        logger.error(f"Error in analyze_and_decide: {e}", exc_info=True)

        # Send error response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "decision_response",
                "error": str(e),
                "decision": {"decision": "error", "actions": [], "reasoning": str(e)},
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )


async def handle_evaluate_context(message: A2AMessage):
    """Handle context evaluation request"""
    logger.info("Evaluating context...")

    try:
        context = message.payload.get("context", {})

        # Use AI to evaluate context
        evaluation = await ai_service.evaluate_context(context)

        # Send response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "evaluation_response",
                "evaluation": evaluation,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )

    except Exception as e:
        logger.error(f"Error in evaluate_context: {e}", exc_info=True)


async def handle_test_message(message: A2AMessage):
    """Handle test messages"""
    logger.info(f"Received test message: {message.payload}")

    # Send response back
    await a2a_client.send_message(
        to_agent=message.from_agent,
        payload={
            "result": "Test received by Decision Agent!",
            "ai_enabled": ai_service.enabled,
            "original_payload": message.payload,
        },
        message_type=MessageType.RESPONSE,
        callback_id=message.message_id,
    )


# === API Endpoints ===


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "agent": "decision",
        "status": "running",
        "version": "1.0.0",
        "ai_enabled": ai_service.enabled,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_status = "connected" if a2a_client and a2a_client.redis_client else "disconnected"

    return {
        "status": "healthy",
        "agent": settings.agent_name,
        "redis": redis_status,
        "ai_service": "enabled" if ai_service.enabled else "disabled",
        "environment": settings.environment,
    }


@app.post("/decide")
async def make_decision(request: DecisionRequest):
    """
    Direct endpoint to make a decision using AI

    This allows testing the decision-making without going through A2A protocol.
    """
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI service is not available")

    try:
        result = await ai_service.analyze_task(request.task, request.context)
        return {
            "status": "success",
            "decision": result,
        }

    except Exception as e:
        logger.error(f"Error making decision: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.post("/evaluate")
async def evaluate(request: EvaluationRequest):
    """
    Direct endpoint to evaluate context

    Allows testing context evaluation without A2A protocol.
    """
    if not ai_service.enabled:
        raise HTTPException(status_code=503, detail="AI service is not available")

    try:
        result = await ai_service.evaluate_context(request.context)
        return {
            "status": "success",
            "evaluation": result,
        }

    except Exception as e:
        logger.error(f"Error evaluating context: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get decision agent status"""
    return {
        "agent": settings.agent_name,
        "environment": settings.environment,
        "ai_service": {
            "enabled": ai_service.enabled,
            "model": "gemini-2.0-flash-exp" if ai_service.enabled else None,
        },
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "listening": a2a_client._listening if a2a_client else False,
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8001,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
