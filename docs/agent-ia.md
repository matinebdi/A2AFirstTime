# AI Agent and PageContext - VacanceAI

![AI Agent Diagram](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090149.png)

The VacanceAI AI assistant is powered by Google Gemini 2.0 Flash and orchestrated via LangChain + LangGraph. It is context-aware: it knows the page the user is viewing and the data displayed.

---

## Agent Architecture

### Orchestrator (`agents/orchestrator/agent.py`)
LangGraph coordinator agent that receives user messages and routes them to the most appropriate agent:
- **UI Agent**: for interface actions (search, booking, navigation)
- **Database Agent**: for complex data queries

### UI Agent (`agents/ui/agent.py`)
ReAct agent with in-memory checkpointer (MemorySaver). It uses Gemini to understand requests and call the appropriate tools. The checkpointer maintains conversation context (lost on pod restart).

### Database Agent (`agents/database/agent.py`)
Specialized agent for Oracle queries via LangChain tools.

---

## UI Agent Tools

| Tool | Description |
|------|-------------|
| `search_vacation` | Search packages with filters (destination, price, duration) |
| `show_package_details` | Display details of a specific package |
| `create_booking_action` | Create a booking directly |
| `start_booking_flow` | Open the booking form for a package |
| `add_to_favorites_action` | Add a package to favorites |
| `navigate_to_page` | Navigate the frontend to a page |
| `show_recommendations` | Display personalized recommendations |

Tools that return an `action` key trigger a UI action in the frontend (navigation, card display, etc.).

---

## PageContext System

### How It Works

1. **`PageContext`** (React Context) stores current page information
2. Each page updates this context via `useSetPageContext()` in a `useEffect`
3. **`ChatWidget`** reads `usePageContext()` and sends it with every WebSocket message
4. The backend (orchestrator) extracts `context.get("page")` and passes it to the UI agent
5. The UI agent appends `[Current page: {...}]` to the `HumanMessage`
6. The agent uses this data to resolve implicit references ("this one", "the first one", "my last booking")

### Data Sent Per Page

| Page | Data |
|------|------|
| Home | `featured_packages: [{id, name}]` |
| Search | `filters: {destination, min_price, ...}`, `results: [{id, name, price}]` |
| PackageDetail | `package_id, package_name, destination, price, duration` |
| Bookings | `bookings: [{id, package_name, status, start_date}]` |
| Hotels | `hotels: [{location_id, name, country, rating}]` |
| HotelDetail | `location_id, hotel_name, country, rating` |

### Usage Examples

- On **PackageDetail**: "book this one for 2 people on June 15th" -> the agent knows the displayed package
- On **Search**: "show me more details on the first one" -> the agent knows the search results
- On **Bookings**: "cancel my last booking" -> the agent sees the bookings list

---

## Automatic Navigation After Action

When the agent performs certain actions, the `ChatWidget` automatically navigates the user to the relevant page:

| Agent Action | Automatic Navigation |
|-------------|---------------------|
| Booking confirmed (`booking_confirmed`) | `/bookings` |
| Added to favorites (`add_favorite`) | `/favorites` |

After `add_favorite`, the ChatWidget also calls `favoritesApi.add()` to persist the favorite client-side before navigating.

---

## WebSocket Message Format

### Send (client -> server)

```json
{
  "message": "Book this one for 2 people on June 15th",
  "context": {
    "user": {"id": "abc-123", "email": "user@example.com"},
    "page": {
      "page": "package_detail",
      "data": {
        "package_id": "pkg-456",
        "package_name": "Bali Explorer",
        "destination": "Indonesia",
        "price": 1299.99,
        "duration": 7
      }
    }
  }
}
```

### Receive (server -> client)

```json
{
  "response": "Booking confirmed for 2 people on June 15th!",
  "ui_actions": [
    {
      "action": "booking_confirmed",
      "data": {"booking_id": "book-789", "package_name": "Bali Explorer"}
    }
  ],
  "agent_type": "ui",
  "timestamp": "2026-02-13T10:30:00Z"
}
```

---

## LangGraph Studio

LangGraph Studio provides a visual interface for debugging and testing agents via [LangSmith](https://smith.langchain.com).

### Setup

- **Image**: `vacanceai-langgraph:latest` (`backend/Dockerfile.langgraph`)
- **Runtime**: `langgraph-cli[inmem]` in dev mode with Cloudflare Tunnel
- **Config**: `backend/langgraph.json` defines 3 graphs:
  - `orchestrator` - Main coordinator agent
  - `ui_agent` - UI interaction agent (without custom checkpointer)
  - `database_agent` - Database query agent (without custom checkpointer)
- **Graph exports**: `backend/agents/studio.py` re-creates agents without custom checkpointers (LangGraph API handles persistence internally)

### Environment Variables

| Variable | Description |
|----------|-------------|
| `LANGCHAIN_API_KEY` | LangSmith API key (tracing) |
| `LANGSMITH_API_KEY` | LangGraph Studio tunnel auth (same key as LANGCHAIN_API_KEY) |

### Access

1. Deploy: `kubectl apply -f k8s/langgraph-studio.yaml`
2. Get tunnel URL from pod logs: `kubectl logs -n vacanceai deploy/langgraph-studio | grep trycloudflare`
3. Open: `https://smith.langchain.com/studio/?baseUrl=<TUNNEL_URL>`

---

## Key Files

| File | Description |
|------|-------------|
| `backend/agents/base.py` | LLM configuration (Gemini 2.0 Flash) |
| `backend/agents/orchestrator/agent.py` | LangGraph orchestrator |
| `backend/agents/ui/agent.py` | UI agent (ReAct + MemorySaver) |
| `backend/agents/ui/tools.py` | UI tools (search, book, navigate, etc.) |
| `backend/agents/database/agent.py` | Database agent |
| `backend/agents/database/tools.py` | DB tools (search, booking, favorites) |
| `frontend/src/contexts/PageContext.tsx` | React Context for current page |
| `frontend/src/components/chat/ChatWidget.tsx` | Chat widget (WebSocket + PageContext) |
| `backend/api/routes/conversations.py` | WebSocket + REST route for chat |
| `backend/agents/studio.py` | Graph exports for LangGraph Studio (no custom checkpointers) |
| `backend/langgraph.json` | LangGraph Studio config (3 graphs) |
| `backend/Dockerfile.langgraph` | LangGraph Studio Docker image |
| `k8s/langgraph-studio.yaml` | K8s deployment + NodePort service |
