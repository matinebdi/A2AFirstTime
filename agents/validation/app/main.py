"""Validation Agent - Action verification and result validation"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

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

# Validation history
validation_history = []


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global a2a_client

    # Startup
    logger.info("🚀 Starting Validation Agent...")

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
        a2a_client.register_handler("verify_action", handle_verify_action)
        a2a_client.register_handler("check_ui_state", handle_check_ui_state)
        a2a_client.register_handler("test", handle_test_message)

        # Start listening in background
        asyncio.create_task(a2a_client.listen())

        logger.info("✅ Validation Agent is ready!")

    except Exception as e:
        logger.error(f"❌ Failed to start Validation Agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Validation Agent...")
    if a2a_client:
        await a2a_client.disconnect()


app = FastAPI(
    title="Validation Agent",
    description="Action verification agent for A2A multi-agent system",
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


class ValidationRequest(BaseModel):
    """Request to validate an action"""
    action: str
    expected_result: str = None


# === Helper Functions ===


def store_validation(action: str, result: str, success: bool):
    """Store validation result in history"""
    validation_history.append({
        "action": action,
        "result": result,
        "success": success,
        "timestamp": datetime.utcnow().isoformat()
    })

    # Keep only last 100 validations
    if len(validation_history) > 100:
        validation_history.pop(0)


def validate_action_result(action: str, params: dict) -> dict:
    """
    Validate that an action was successful

    In production, this would check actual UI state, database records, etc.
    """
    action_lower = action.lower()

    # Simulate validation logic
    if "fill" in action_lower:
        field = params.get("field", "")
        value = params.get("value", "")

        if field and value:
            return {
                "valid": True,
                "message": f"Field '{field}' successfully filled with value '{value}'",
                "confidence": 0.95
            }
        else:
            return {
                "valid": False,
                "message": "Missing field or value",
                "confidence": 1.0
            }

    elif "click" in action_lower or "button" in action_lower:
        return {
            "valid": True,
            "message": "Button click action successful",
            "confidence": 0.90
        }

    elif "navigate" in action_lower or "url" in action_lower:
        return {
            "valid": True,
            "message": "Navigation successful",
            "confidence": 0.85
        }

    else:
        return {
            "valid": True,
            "message": f"Action '{action}' completed",
            "confidence": 0.80
        }


# === Message Handlers ===


async def handle_verify_action(message: A2AMessage):
    """
    Handle verify_action request

    Verifies that an action was successfully completed
    """
    logger.info("Verifying action...")

    try:
        params = message.payload.get("params", {})
        action = params.get("action", "unknown")

        # Validate the action
        validation_result = validate_action_result(action, params)

        # Store validation
        store_validation(action, validation_result["message"], validation_result["valid"])

        # Send response back
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "validation_response",
                "action": action,
                "validation": validation_result,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
            correlation_id=message.correlation_id,
        )

        status = "✅ VALID" if validation_result["valid"] else "❌ INVALID"
        logger.info(f"Validation result: {status} - {validation_result['message']}")

    except Exception as e:
        logger.error(f"Error in verify_action: {e}", exc_info=True)

        # Send error response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "validation_response",
                "error": str(e),
                "validation": {"valid": False, "message": str(e)}
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )


async def handle_check_ui_state(message: A2AMessage):
    """Handle UI state check request"""
    logger.info("Checking UI state...")

    try:
        expected_state = message.payload.get("expected_state", {})

        # Simulate UI state check
        ui_state_result = {
            "current_state": "ready",
            "matches_expected": True,
            "differences": [],
        }

        # Send response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "ui_state_response",
                "state": ui_state_result,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )

        logger.info(f"UI state check: matches_expected={ui_state_result['matches_expected']}")

    except Exception as e:
        logger.error(f"Error in check_ui_state: {e}", exc_info=True)


async def handle_test_message(message: A2AMessage):
    """Handle test messages"""
    logger.info(f"Received test message: {message.payload}")

    await a2a_client.send_message(
        to_agent=message.from_agent,
        payload={
            "result": "Test received by Validation Agent!",
            "total_validations": len(validation_history),
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
        "agent": "validation",
        "status": "running",
        "version": "1.0.0",
        "total_validations": len(validation_history),
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
        "total_validations": len(validation_history),
    }


@app.post("/validate")
async def validate(request: ValidationRequest):
    """
    Direct endpoint to validate an action

    Allows testing validation without A2A protocol.
    """
    try:
        result = validate_action_result(request.action, {})

        return {
            "status": "success",
            "action": request.action,
            "validation": result,
        }

    except Exception as e:
        logger.error(f"Error validating action: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/history")
async def get_history():
    """Get validation history"""
    return {
        "total_validations": len(validation_history),
        "validations": validation_history[-20:]  # Last 20 validations
    }


@app.get("/status")
async def get_status():
    """Get validation agent status"""
    successful = sum(1 for v in validation_history if v.get("success"))
    failed = len(validation_history) - successful

    return {
        "agent": settings.agent_name,
        "environment": settings.environment,
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "listening": a2a_client._listening if a2a_client else False,
        "statistics": {
            "total_validations": len(validation_history),
            "successful": successful,
            "failed": failed,
            "success_rate": f"{(successful / len(validation_history) * 100):.1f}%" if validation_history else "N/A"
        }
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8004,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
