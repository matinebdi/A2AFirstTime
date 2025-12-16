"""Form Agent - Form filling with database persistence"""

import asyncio
import logging
from contextlib import asynccontextmanager
from datetime import datetime

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from faker import Faker

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

# Global A2A client and faker
a2a_client: A2AClient = None
fake = Faker()

# In-memory form data storage (in production, would use Oracle DB)
form_data_storage = {}


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Lifecycle management for the FastAPI app"""
    global a2a_client

    # Startup
    logger.info("🚀 Starting Form Agent...")

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
        a2a_client.register_handler("fill_field", handle_fill_field)
        a2a_client.register_handler("get_form_data", handle_get_form_data)
        a2a_client.register_handler("test", handle_test_message)

        # Start listening in background
        asyncio.create_task(a2a_client.listen())

        logger.info("✅ Form Agent is ready!")

    except Exception as e:
        logger.error(f"❌ Failed to start Form Agent: {e}")
        raise

    yield

    # Shutdown
    logger.info("🛑 Shutting down Form Agent...")
    if a2a_client:
        await a2a_client.disconnect()


app = FastAPI(
    title="Form Agent",
    description="Form filling agent with database persistence for A2A multi-agent system",
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


class FormFillRequest(BaseModel):
    """Request to fill a form field"""
    field: str
    value: str = None


# === Helper Functions ===


def generate_form_value(field_name: str) -> str:
    """Generate realistic form data based on field name"""
    field_lower = field_name.lower()

    if "username" in field_lower or "user" in field_lower:
        return fake.user_name()
    elif "email" in field_lower:
        return fake.email()
    elif "password" in field_lower or "pass" in field_lower:
        return fake.password(length=12)
    elif "phone" in field_lower or "mobile" in field_lower:
        return fake.phone_number()
    elif "firstname" in field_lower or "first_name" in field_lower:
        return fake.first_name()
    elif "lastname" in field_lower or "last_name" in field_lower:
        return fake.last_name()
    elif "name" in field_lower:
        return fake.name()
    elif "address" in field_lower:
        return fake.address().replace("\n", ", ")
    elif "city" in field_lower:
        return fake.city()
    elif "country" in field_lower:
        return fake.country()
    elif "zipcode" in field_lower or "postal" in field_lower:
        return fake.postcode()
    elif "company" in field_lower or "organization" in field_lower:
        return fake.company()
    elif "job" in field_lower or "title" in field_lower:
        return fake.job()
    elif "url" in field_lower or "website" in field_lower:
        return fake.url()
    else:
        return fake.word()


def store_form_data(session_id: str, field: str, value: str):
    """Store form data in memory (would use Oracle in production)"""
    if session_id not in form_data_storage:
        form_data_storage[session_id] = {}

    form_data_storage[session_id][field] = {
        "value": value,
        "timestamp": datetime.utcnow().isoformat()
    }

    logger.info(f"Stored form data for session {session_id}: {field}={value}")


def get_stored_form_data(session_id: str) -> dict:
    """Retrieve stored form data"""
    return form_data_storage.get(session_id, {})


# === Message Handlers ===


async def handle_fill_field(message: A2AMessage):
    """
    Handle fill_field request

    Fills a form field with appropriate data
    """
    logger.info("Filling form field...")

    try:
        params = message.payload.get("params", {})
        field = params.get("field", "")
        value = params.get("value")
        correlation_id = message.correlation_id or "default_session"

        # If no value provided, generate one
        if not value:
            value = generate_form_value(field)
            logger.info(f"Generated value for {field}: {value}")
        else:
            logger.info(f"Using provided value for {field}: {value}")

        # Store form data
        store_form_data(correlation_id, field, value)

        # Send response back
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "form_response",
                "field": field,
                "value": value,
                "status": "filled",
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
            correlation_id=message.correlation_id,
        )

        logger.info(f"Form field filled: {field}={value}")

    except Exception as e:
        logger.error(f"Error in fill_field: {e}", exc_info=True)

        # Send error response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "form_response",
                "error": str(e),
                "status": "error"
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )


async def handle_get_form_data(message: A2AMessage):
    """Handle request to retrieve stored form data"""
    logger.info("Retrieving form data...")

    try:
        session_id = message.payload.get("session_id", message.correlation_id or "default_session")
        form_data = get_stored_form_data(session_id)

        # Send response
        await a2a_client.send_message(
            to_agent=message.from_agent,
            payload={
                "task": "form_data_response",
                "session_id": session_id,
                "form_data": form_data,
            },
            message_type=MessageType.RESPONSE,
            callback_id=message.message_id,
        )

        logger.info(f"Retrieved {len(form_data)} form fields for session {session_id}")

    except Exception as e:
        logger.error(f"Error in get_form_data: {e}", exc_info=True)


async def handle_test_message(message: A2AMessage):
    """Handle test messages"""
    logger.info(f"Received test message: {message.payload}")

    await a2a_client.send_message(
        to_agent=message.from_agent,
        payload={
            "result": "Test received by Form Agent!",
            "stored_sessions": len(form_data_storage),
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
        "agent": "form",
        "status": "running",
        "version": "1.0.0",
        "stored_sessions": len(form_data_storage),
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
        "stored_sessions": len(form_data_storage),
    }


@app.post("/fill")
async def fill_form(request: FormFillRequest):
    """
    Direct endpoint to fill a form field

    Allows testing form filling without A2A protocol.
    """
    try:
        value = request.value or generate_form_value(request.field)

        return {
            "status": "success",
            "field": request.field,
            "value": value,
        }

    except Exception as e:
        logger.error(f"Error filling form: {e}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/data/{session_id}")
async def get_data(session_id: str):
    """Get stored form data for a session"""
    form_data = get_stored_form_data(session_id)

    if not form_data:
        raise HTTPException(status_code=404, detail="Session not found")

    return {
        "session_id": session_id,
        "form_data": form_data,
    }


@app.get("/status")
async def get_status():
    """Get form agent status"""
    return {
        "agent": settings.agent_name,
        "environment": settings.environment,
        "redis_host": settings.redis_host,
        "redis_port": settings.redis_port,
        "listening": a2a_client._listening if a2a_client else False,
        "stored_sessions": len(form_data_storage),
    }


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8003,
        reload=settings.debug,
        log_level=settings.log_level.lower(),
    )
