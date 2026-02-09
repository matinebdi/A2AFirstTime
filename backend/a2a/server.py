"""Google A2A Protocol - Server endpoints"""

from fastapi import APIRouter, HTTPException, BackgroundTasks
from typing import Dict
from .protocol import (
    AgentCard, AgentCapabilities, Skill, Task, TaskInput,
    TaskOutput, TaskState, TaskCreateRequest, TaskStatusResponse
)

# Task storage (in production, use Redis or database)
tasks: Dict[str, Task] = {}

# Define the agent card
AGENT_CARD = AgentCard(
    name="vacanceai-orchestrator",
    description="VacanceAI Orchestrator Agent - Routes requests to specialized agents",
    url="http://localhost:8000",
    version="1.0.0",
    capabilities=AgentCapabilities(
        streaming=True,
        push_notifications=False,
        state_persistence=True
    ),
    skills=[
        Skill(
            id="search_vacations",
            name="Search Vacations",
            description="Search for vacation packages based on user preferences"
        ),
        Skill(
            id="book_package",
            name="Book Package",
            description="Create a booking for a vacation package"
        ),
        Skill(
            id="get_recommendations",
            name="Get Recommendations",
            description="Get personalized vacation recommendations"
        ),
        Skill(
            id="chat_assistant",
            name="Chat Assistant",
            description="Interactive vacation planning assistant"
        )
    ]
)

a2a_router = APIRouter()


@a2a_router.get("/.well-known/agent.json")
async def get_agent_card() -> AgentCard:
    """Return the agent card (A2A discovery endpoint)"""
    return AGENT_CARD


@a2a_router.post("/a2a/tasks")
async def create_task(
    request: TaskCreateRequest,
    background_tasks: BackgroundTasks
) -> Task:
    """Create a new task"""
    task = Task(
        input=TaskInput(
            skill_id=request.skill_id,
            message=request.message,
            context=request.context
        )
    )

    tasks[task.id] = task

    # Process task in background
    background_tasks.add_task(process_task, task.id)

    return task


@a2a_router.get("/a2a/tasks/{task_id}")
async def get_task(task_id: str) -> Task:
    """Get task status"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    return tasks[task_id]


@a2a_router.post("/a2a/tasks/{task_id}/cancel")
async def cancel_task(task_id: str) -> Task:
    """Cancel a running task"""
    if task_id not in tasks:
        raise HTTPException(status_code=404, detail="Task not found")

    task = tasks[task_id]

    if task.state not in [TaskState.PENDING, TaskState.RUNNING]:
        raise HTTPException(
            status_code=400,
            detail=f"Cannot cancel task in state: {task.state}"
        )

    task.cancel()
    return task


@a2a_router.get("/a2a/tasks")
async def list_tasks(
    state: TaskState = None,
    limit: int = 20,
    offset: int = 0
) -> Dict:
    """List tasks with optional filtering"""
    filtered = list(tasks.values())

    if state:
        filtered = [t for t in filtered if t.state == state]

    # Sort by created_at descending
    filtered.sort(key=lambda t: t.created_at, reverse=True)

    # Apply pagination
    paginated = filtered[offset:offset + limit]

    return {
        "tasks": paginated,
        "total": len(filtered),
        "limit": limit,
        "offset": offset
    }


async def process_task(task_id: str):
    """Process a task (placeholder - will be implemented with LangGraph agents)"""
    if task_id not in tasks:
        return

    task = tasks[task_id]
    task.start()

    try:
        # Import here to avoid circular imports
        from agents.orchestrator.agent import process_request

        # Process with orchestrator agent
        result = await process_request(
            message=task.input.message,
            skill_id=task.input.skill_id,
            context=task.input.context
        )

        task.complete(TaskOutput(
            message=result.get("response", "Task completed"),
            artifacts=result.get("artifacts", []),
            metadata=result.get("metadata")
        ))

    except ImportError:
        # Agents not yet implemented - return placeholder
        task.complete(TaskOutput(
            message=f"Processed: {task.input.message}",
            metadata={"note": "Agents not yet implemented"}
        ))

    except Exception as e:
        task.fail(str(e))
