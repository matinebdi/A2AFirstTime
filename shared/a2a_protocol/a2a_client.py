"""A2A Client - Redis Pub/Sub Communication (Shared)"""

import asyncio
import json
import logging
from typing import Callable, Optional

import redis.asyncio as redis

from .schemas import A2AMessage, MessageType, Priority

logger = logging.getLogger(__name__)


class A2AClient:
    """Client for Agent-to-Agent communication via Redis Pub/Sub"""

    def __init__(self, agent_name: str, redis_host: str, redis_port: int,
                 redis_password: str = "", redis_db: int = 0,
                 channel_prefix: str = "agent"):
        self.redis_client: Optional[redis.Redis] = None
        self.pubsub: Optional[redis.client.PubSub] = None
        self.agent_name = agent_name
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_password = redis_password
        self.redis_db = redis_db
        self.channel_prefix = channel_prefix
        self.message_handlers: dict[str, Callable] = {}
        self._listening = False

    async def connect(self):
        """Connect to Redis"""
        try:
            self.redis_client = redis.Redis(
                host=self.redis_host,
                port=self.redis_port,
                password=self.redis_password if self.redis_password else None,
                db=self.redis_db,
                decode_responses=True,
            )
            await self.redis_client.ping()
            logger.info(f"✅ Connected to Redis at {self.redis_host}:{self.redis_port}")

            # Create pubsub
            self.pubsub = self.redis_client.pubsub()
            await self.pubsub.subscribe(f"{self.channel_prefix}:{self.agent_name}")
            logger.info(f"📡 Subscribed to channel: {self.channel_prefix}:{self.agent_name}")

        except Exception as e:
            logger.error(f"❌ Failed to connect to Redis: {e}")
            raise

    async def disconnect(self):
        """Disconnect from Redis"""
        self._listening = False
        if self.pubsub:
            await self.pubsub.unsubscribe()
            await self.pubsub.close()
        if self.redis_client:
            await self.redis_client.close()
        logger.info("Disconnected from Redis")

    async def send_message(
        self,
        to_agent: str,
        payload: dict,
        message_type: MessageType = MessageType.REQUEST,
        priority: Priority = Priority.NORMAL,
        callback_id: Optional[str] = None,
        correlation_id: Optional[str] = None,
    ) -> A2AMessage:
        """Send a message to another agent"""
        message = A2AMessage(
            from_agent=self.agent_name,
            to_agent=to_agent,
            message_type=message_type,
            payload=payload,
            callback_id=callback_id,
            correlation_id=correlation_id,
            priority=priority,
        )

        channel = f"{self.channel_prefix}:{to_agent}"
        message_json = json.dumps(message.to_dict())

        await self.redis_client.publish(channel, message_json)
        logger.info(
            f"📤 Sent {message_type.value} to {to_agent}: {message.message_id}"
        )

        return message

    def register_handler(self, message_type: str, handler: Callable):
        """Register a handler for a specific message type"""
        self.message_handlers[message_type] = handler
        logger.info(f"Registered handler for message type: {message_type}")

    async def listen(self):
        """Listen for incoming messages"""
        if not self.pubsub:
            raise RuntimeError("Not connected to Redis. Call connect() first.")

        self._listening = True
        logger.info(f"👂 Listening for messages on {self.channel_prefix}:{self.agent_name}...")

        try:
            async for message in self.pubsub.listen():
                if not self._listening:
                    break

                if message["type"] == "message":
                    await self._handle_message(message["data"])

        except asyncio.CancelledError:
            logger.info("Listening task cancelled")
        except Exception as e:
            logger.error(f"Error in listen loop: {e}")
            raise

    async def _handle_message(self, raw_message: str):
        """Handle incoming message"""
        try:
            message_data = json.loads(raw_message)
            message = A2AMessage.from_dict(message_data)

            logger.info(
                f"📥 Received {message.message_type.value} from {message.from_agent}: {message.message_id}"
            )

            # Get task from payload
            task = message.payload.get("action", message.payload.get("task", "unknown"))

            # Call registered handler
            if task in self.message_handlers:
                await self.message_handlers[task](message)
            else:
                logger.warning(f"No handler registered for task: {task}")

        except Exception as e:
            logger.error(f"Error handling message: {e}", exc_info=True)
