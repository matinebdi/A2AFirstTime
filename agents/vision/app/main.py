"""Vision Agent - UI Analysis with Gemini Vision"""

import asyncio
import logging
from contextlib import asynccontextmanager

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel

import google.generativeai as genai

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
vision_model = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global a2a_client, vision_model

    # Startup
    logger.info("🚀 Starting Vision Agent...")

    # Initialize Gemini Vision
    if settings.google_api_key:
        try:
            genai.configure(api_key=settings.google_api_key)
            vision_model = genai.GenerativeModel("gemini-2.0-flash-exp")
            logger.info("✅ Google Gemini Vision initialized successfully")
        except Exception as e:
            logger.error(f"❌ Failed to initialize Gemini Vision: {e}")
    else:
        logger.warning("⚠️  No Google API Key provided. Vision features disabled.")

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
        a2a_client.register_handler("analyze_ui", handle_analyze_ui)
        a2a_client.register_handler("detect_elements", handle_detect_elements)
        a2a_client.register_handler("test", handle_test_message)

        # Start listening in background
        asyncio.create_task(a2a_client.listen())

        logger.info("✅ Vision Agent is ready!")

    except Exception as e:
        logger.error(f"❌ Failed to start Vision Agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Vision Agent...")
    if a2a_client:
        await a2a_client.disconnect()


app = FastAPI(
    title="Vision Agent",
    description="UI Analysis agent for A2A multi-agent system",
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


class AnalysisRequest(BaseModel):
    """Request for UI analysis"""
    screenshot_url: str = None
    page_html: str = None


# === Message Handlers ===


async def handle_analyze_ui(message: A2AMessage):
    """
    Handle analyze_ui request

    Analyzes UI elements from screenshot or HTML
    """
    logger.info("Analyzing UI...")

    try:
        params = message.payload.get("params", {})

        # Simulate UI analysis (in production, would analyze actual screenshot)
        analysis_result = {
            "status": "success",
            "elements_found": [
                {
                    "type": "input",
                    "id": "username",
                    "label": "Username",
                    "visible": True,
                    "required": True
                },
                {
                    "type": "input",
                    "id": "email",
                    "label": "Email",
                    "visible": True,
                    "required": True
                },
                {
                    "type": "button",
                    "id": "submit",
                    "label": "Register",
                    "visible": True
                }
            ],
            "page_type": "registration_form"
        }

        # If we have Gemini Vision, use it for more advanced analysis
        if vision_model and params.get("use_ai"):
            try:
                prompt = f"""
Analyze this UI context and provide insights:
{params}

Identify form fields, buttons, and interactive elements.
"""
                response = await vision_model.generate_content_async(prompt)
                analysis_result["ai_insights"] = response.text.strip()
            except Exception as e:
                logger.error(f"AI analysis failed: {e}")

        # Send response back
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "vision_response",
                "analysis": analysis_result,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
            correlation_id=message.correlation_id,
        )

        logger.info(f"Vision analysis completed: {len(analysis_result.get('elements_found', []))} elements found")

    except Exception as e:
        logger.error(f"Error in analyze_ui: {e}", exc_info=True)

        # Send error response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "vision_response",
                "error": str(e),
                "analysis": {"status": "error"}
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )


async def handle_detect_elements(message: A2AMessage):
    """Handle element detection request"""
    logger.info("Detecting UI elements...")

    try:
        element_type = message.payload.get("element_type", "all")

        detected_elements = {
            "buttons": ["submit", "cancel", "back"],
            "inputs": ["username", "email", "password"],
            "links": ["forgot_password", "login"]
        }

        # Send response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "detection_response",
                "elements": detected_elements,
                "element_type": element_type,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )

    except Exception as e:
        logger.error(f"Error in detect_elements: {e}", exc_info=True)


async def handle_test_message(message: A2AMessage):
    """Handle test messages"""
    logger.info(f"Received test message: {message.payload}")

    await a2a_client.send_message(
        to_agent=message.from_agent,
        payload={
            "result": "Test received by Vision Agent!",
            "vision_enabled": vision_model is not None,
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
        "agent": "vision",
        "status": "running",
        "version": "1.0.0",
        "vision_enabled": vision_model is not None,
    }


@app.get("/health")
async def health():
    """Health check endpoint"""
    redis_status = "connected" if a2a_client and a2a_client.redis_client else "disconnected"

    return {
        "status": "healthy",
        "agent": settings.agent_name,
        "redis": redis_status,
        "vision_service": "enabled" if vision_model else "disabled",
        "environment": settings.environment,
    }


@app.post("/analyze")
async def analyze(request: AnalysisRequest):
    """
    Direct endpoint to analyze UI

    Allows testing UI analysis without A2A protocol.
    """
    if not vision_model:
        return {
            "status": "success",
            "message": "Vision analysis (mock mode)",
            "elements": ["username", "email", "submit"]
        }

    try:
        # Simulate analysis
        return {
            "status": "success",
            "elements_found": 3,
            "page_type": "form"
        }

    except Exception as e:
        logger.error(f"Error analyzing UI: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/status")
async def get_status():
    """Get vision agent status"""
    return {
        "agent": settings.agent_name,
        "environment": settings.environment,
        "vision_service": {
            "enabled": vision_model is not None,
            "model": "gemini-2.0-flash-exp" if vision_model else None,
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
        port=8002,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
