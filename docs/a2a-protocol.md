# Agent-to-Agent Protocol (A2A) - VacanceAI

The backend uses Google's Agent-to-Agent (A2A) protocol for AI agent coordination.

---

## Agents

| Agent | Role | Technology |
|-------|------|------------|
| **Orchestrator** | Coordinates other agents, routes messages | LangGraph |
| **Database** | Executes Oracle queries | LangChain tools |
| **UI** | User interface actions (search, booking, navigation) | ReAct + MemorySaver |

---

## A2A Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/.well-known/agent.json` | Agent Card (agent metadata) |
| POST | `/a2a/tasks` | Create a new task |
| GET | `/a2a/tasks/{id}` | Retrieve task status |
| POST | `/a2a/tasks/{id}/messages` | Send a message to a task |
| POST | `/a2a/tasks/{id}/cancel` | Cancel a running task |

---

## Agent Card

The Agent Card is a JSON document exposed at `/.well-known/agent.json` that describes the agent's capabilities:

```json
{
  "name": "VacanceAI Assistant",
  "description": "AI assistant for vacation booking",
  "capabilities": ["search", "booking", "navigation", "recommendations"],
  "protocol_version": "1.0"
}
```

---

## Communication Flow

![AI Agent Diagram](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090149.png)

1. The user message arrives via WebSocket
2. The orchestrator classifies the message and routes it to the appropriate agent
3. The agent executes its tools and returns a response
4. The `ui_actions` are sent back to the frontend for execution

---

## Files

| File | Description |
|------|-------------|
| `backend/a2a/protocol.py` | Pydantic schemas for the A2A protocol |
| `backend/a2a/client.py` | A2A client (for calling other agents) |
| `backend/a2a/server.py` | A2A server (exposes endpoints) |
