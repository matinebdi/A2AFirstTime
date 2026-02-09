"""A2A Protocol Client - For agent-to-agent communication"""

import httpx
from typing import Optional, Dict, Any
from .protocol import AgentCard, Task, TaskCreateRequest, TaskStatusResponse, TaskState


class A2AClient:
    """Client for communicating with A2A-compatible agents"""

    def __init__(self, base_url: str, timeout: float = 30.0):
        """Initialize A2A client

        Args:
            base_url: Base URL of the agent (e.g., http://localhost:8001)
            timeout: Request timeout in seconds
        """
        self.base_url = base_url.rstrip("/")
        self.timeout = timeout
        self._client = httpx.AsyncClient(timeout=timeout)

    async def get_agent_card(self) -> AgentCard:
        """Fetch the agent's card (metadata)

        Returns:
            AgentCard with agent information
        """
        response = await self._client.get(
            f"{self.base_url}/.well-known/agent.json"
        )
        response.raise_for_status()
        return AgentCard(**response.json())

    async def create_task(
        self,
        message: str,
        skill_id: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ) -> Task:
        """Create a new task on the agent

        Args:
            message: Task message/instruction
            skill_id: Optional skill ID to invoke
            context: Optional context data

        Returns:
            Created Task object
        """
        request = TaskCreateRequest(
            message=message,
            skill_id=skill_id,
            context=context
        )

        response = await self._client.post(
            f"{self.base_url}/a2a/tasks",
            json=request.model_dump()
        )
        response.raise_for_status()
        return Task(**response.json())

    async def get_task(self, task_id: str) -> TaskStatusResponse:
        """Get task status

        Args:
            task_id: Task ID to query

        Returns:
            TaskStatusResponse with current status
        """
        response = await self._client.get(
            f"{self.base_url}/a2a/tasks/{task_id}"
        )
        response.raise_for_status()
        return TaskStatusResponse(**response.json())

    async def wait_for_completion(
        self,
        task_id: str,
        poll_interval: float = 0.5,
        max_wait: float = 60.0
    ) -> TaskStatusResponse:
        """Wait for task to complete

        Args:
            task_id: Task ID to wait for
            poll_interval: Seconds between status checks
            max_wait: Maximum seconds to wait

        Returns:
            Final TaskStatusResponse

        Raises:
            TimeoutError: If task doesn't complete within max_wait
        """
        import asyncio
        elapsed = 0.0

        while elapsed < max_wait:
            status = await self.get_task(task_id)

            if status.state in (TaskState.COMPLETED, TaskState.FAILED, TaskState.CANCELLED):
                return status

            await asyncio.sleep(poll_interval)
            elapsed += poll_interval

        raise TimeoutError(f"Task {task_id} did not complete within {max_wait} seconds")

    async def send_message(
        self,
        task_id: str,
        message: str
    ) -> Task:
        """Send a follow-up message to an existing task

        Args:
            task_id: Task ID
            message: Message content

        Returns:
            Updated Task object
        """
        response = await self._client.post(
            f"{self.base_url}/a2a/tasks/{task_id}/messages",
            json={"message": message}
        )
        response.raise_for_status()
        return Task(**response.json())

    async def cancel_task(self, task_id: str) -> TaskStatusResponse:
        """Cancel a task

        Args:
            task_id: Task ID to cancel

        Returns:
            TaskStatusResponse with cancelled status
        """
        response = await self._client.post(
            f"{self.base_url}/a2a/tasks/{task_id}/cancel"
        )
        response.raise_for_status()
        return TaskStatusResponse(**response.json())

    async def close(self):
        """Close the HTTP client"""
        await self._client.aclose()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.close()
