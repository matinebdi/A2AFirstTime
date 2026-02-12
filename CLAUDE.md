# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**VacanceAI** is a vacation booking platform with an AI-powered chatbot assistant. The application allows users to browse vacation packages, make bookings, leave reviews, and interact with an intelligent assistant that can help find the perfect vacation. The AI agent has full page context awareness and can act on displayed data.

## Tech Stack

- **Backend**: Python 3.12 / FastAPI / Uvicorn
- **Frontend**: React 18 + TypeScript + Vite + Tailwind CSS + Framer Motion
- **Database**: Oracle 21c XE (SQLAlchemy ORM + oracledb thin mode)
- **AI**: Google Gemini 2.0 Flash (LangChain + LangGraph)
- **Auth**: Custom JWT (PyJWT + passlib bcrypt)
- **Observability**: OpenTelemetry + Jaeger
- **Logging**: Centralized RotatingFileHandler (app, agents, sql, errors)
- **Containerization**: Docker Compose (Oracle DB) + Kubernetes (app)

## Architecture

```
Kubernetes (namespace: vacanceai)
  Ingress NGINX (localhost:80)
    /api/* -> backend:8000
    /*     -> frontend:80 (nginx)
  Jaeger (traces) -> :16686 (NodePort 31686)

Docker Compose
  Oracle 21c XE -> localhost:1521/XE
  Backend connects via host.docker.internal:1521

Logs (hostPath volume)
  backend pod /app/log_apps -> backend/log_apps/ (local repo)
```

## Development Commands

```bash
# Automated setup (recommended)
.\setup.ps1                      # Full setup: Oracle + build + K8s
.\setup.ps1 -SkipOracle          # Skip Oracle startup
.\setup.ps1 -SkipBuild           # Skip Docker image builds
.\setup.ps1 -SkipSchema          # Skip Oracle schema init

# Start Oracle (required first)
docker compose up -d

# Build images
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend

# Deploy to Kubernetes
kubectl apply -f k8s/

# Restart after code changes
docker build -t vacanceai-backend ./backend && kubectl rollout restart deploy/backend -n vacanceai
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend && kubectl rollout restart deploy/frontend -n vacanceai

# View logs (kubectl)
kubectl logs -n vacanceai deploy/backend -f
kubectl logs -n vacanceai deploy/frontend -f

# View logs (local files - mounted from K8s pod)
cat backend/log_apps/app.log      # General app logs
cat backend/log_apps/sql.log      # All SQL queries
cat backend/log_apps/agents.log   # AI agent activity
cat backend/log_apps/errors.log   # Errors only

# Run backend locally (without Docker/K8s)
cd backend && uvicorn api.main:app --reload --port 8000

# Run frontend locally (without Docker/K8s)
cd frontend && npm install && npm run dev
```

### URLs (Kubernetes)

- **Frontend**: http://localhost
- **Backend API**: http://localhost/api/health
- **Swagger**: http://localhost/swagger
- **ReDoc**: http://localhost/redoc
- **Jaeger UI**: http://localhost:31686
- **Oracle**: localhost:1521/XE

### URLs (Local dev)

- **Backend**: http://localhost:8000
- **Frontend**: http://localhost:5173

## Backend Structure

```
backend/
├── api/
│   ├── main.py                 # FastAPI app entry point (setup_logging at startup)
│   └── routes/
│       ├── auth.py             # JWT authentication
│       ├── packages.py         # Vacation packages CRUD
│       ├── bookings.py         # User bookings
│       ├── favorites.py        # User favorites
│       ├── reviews.py          # Package reviews
│       ├── destinations.py     # Destinations
│       ├── conversations.py    # Chat IA (WebSocket + REST)
│       ├── tripadvisor.py      # TripAdvisor hotel data
│       └── health.py           # Health + Readiness probes
├── agents/
│   ├── base.py                 # LLM config (Gemini)
│   ├── orchestrator/agent.py   # LangGraph orchestrator (routes to DB or UI agent)
│   ├── database/
│   │   ├── agent.py            # Database agent
│   │   └── tools.py            # DB tools (search, booking, favorites)
│   └── ui/
│       ├── agent.py            # UI agent (ReAct with checkpointer)
│       └── tools.py            # UI tools (search_vacation, create_booking_action, etc.)
├── a2a/                        # Agent-to-Agent protocol
│   ├── protocol.py
│   ├── client.py
│   └── server.py
├── auth/
│   ├── jwt_service.py          # JWT token service (PyJWT + bcrypt)
│   └── middleware.py           # Auth middleware (get_current_user, get_optional_user)
├── database/
│   ├── models.py               # SQLAlchemy ORM models (11 models + to_dict methods)
│   ├── session.py              # Engine + SessionLocal + get_db dependency
│   ├── types.py                # Custom types (JSONEncodedCLOB, OracleBoolean)
│   └── oracle_schema.sql       # Full schema (11 tables + triggers)
├── logging_config.py           # Centralized logging (RotatingFileHandler -> log_apps/)
├── log_apps/                   # Log output directory (mounted via K8s hostPath volume)
│   ├── app.log                 # General app logs (INFO+)
│   ├── agents.log              # AI agent activity (DEBUG+)
│   ├── sql.log                 # All SQL queries (DEBUG+)
│   └── errors.log              # Errors only (ERROR+)
├── config.py                   # Settings (pydantic-settings)
├── telemetry.py                # OpenTelemetry setup
├── requirements.txt
└── Dockerfile
```

## Frontend Structure

```
frontend/src/
├── components/
│   ├── Layout.tsx              # Main layout (AnimatedBackground + Header + AnimatePresence + Outlet + Footer)
│   ├── animations/
│   │   ├── index.ts            # Re-exports all animation components
│   │   ├── FadeIn.tsx          # Scroll reveal wrapper (direction, delay, duration)
│   │   ├── StaggerContainer.tsx # Staggered list/grid animations
│   │   ├── PageTransition.tsx  # Page entry animation wrapper
│   │   ├── HeroCarousel.tsx    # Ken Burns carousel (4 images, crossfade)
│   │   ├── HeroVideo.tsx       # Video background (unused, available)
│   │   ├── AnimatedButton.tsx  # Button hover/tap effects (scale + glow)
│   │   └── AnimatedBackground.tsx # Full-app Ken Burns background (fixed, 5 images)
│   ├── common/
│   │   ├── Header.tsx
│   │   └── Footer.tsx
│   ├── chat/
│   │   ├── ChatWidget.tsx      # Floating chat widget (WebSocket)
│   │   └── ChatErrorBoundary.tsx
│   ├── search/
│   │   ├── DualRangeSlider.tsx # Price/duration range slider
│   │   ├── TagFilter.tsx       # Tag selection filter
│   │   ├── ActiveFilters.tsx   # Active filter badges
│   │   └── Pagination.tsx      # Page navigation
│   └── packages/
│       └── PackageCard.tsx     # 3D tilt effect (react-parallax-tilt)
├── pages/
│   ├── Home.tsx                # Landing page (hero carousel + featured packages)
│   ├── Search.tsx              # Package search (dual sliders, tags, pagination, URL state)
│   ├── Favorites.tsx           # User's favorite packages
│   ├── PackageDetail.tsx       # Single package view + booking form
│   ├── Hotels.tsx              # TripAdvisor hotels grid (3-col cards, single API call)
│   ├── HotelDetail.tsx         # Single hotel with photos + progressive review reveal
│   ├── Bookings.tsx            # User's bookings (AG Grid)
│   ├── Profile.tsx             # User profile + avatar upload
│   ├── Login.tsx
│   └── SignUp.tsx
├── contexts/
│   ├── AuthContext.tsx          # Auth state (JWT tokens in localStorage)
│   └── PageContext.tsx          # Current page context for AI agent
├── hooks/
│   └── useChat.ts              # WebSocket chat hook
├── services/
│   ├── api.ts                  # REST API client
│   └── tripadvisor.ts          # TripAdvisor API client
├── utils/
│   ├── uuid.ts
│   └── telemetry.ts            # OpenTelemetry browser traces
├── types/index.ts
├── App.tsx                     # Router + Providers
└── main.tsx                    # Entry point
```

## Database (Oracle 21c XE + SQLAlchemy ORM)

- **Connection**: `localhost:1521/XE`, user `VACANCEAI` / `vacanceai`
- **SYS password**: `admin`
- **Schema**: `backend/database/oracle_schema.sql` (11 tables + triggers)
- **ORM**: `backend/database/models.py` (11 SQLAlchemy models with relationships + `to_dict()` methods)
- **Session**: `backend/database/session.py` (engine, `SessionLocal`, `get_db` FastAPI dependency, `create_session` for WebSocket/agents)
- **Custom types**: `backend/database/types.py` (`JSONEncodedCLOB` for JSON<->CLOB, `OracleBoolean` for bool<->NUMBER(1))

### Key patterns
- JSON stored in CLOB; auto-serialized by `JSONEncodedCLOB` type decorator
- BOOLEAN mapped via `OracleBoolean` type decorator (bool <-> NUMBER(1))
- UUID -> VARCHAR2(36) + SYS_GUID() (server_default)
- Relationships with `joinedload()` to avoid N+1 queries
- `to_dict()`, `to_dict_with_destination()`, `to_dict_with_joins()` methods on models for API serialization
- Decimal -> float conversion in `to_dict()` via `_f()` helper
- Routes use `db: Session = Depends(get_db)` for session management
- Agent tools use `create_session()` (manual session, try/finally)
- WebSocket uses `create_session()` per message (not per connection)
- `updated_at` managed by Oracle triggers, not SQLAlchemy

### Tables

| Table | Description |
|-------|-------------|
| `users` | User accounts |
| `refresh_tokens` | JWT refresh tokens |
| `destinations` | Travel destinations (15 countries) |
| `packages` | Vacation packages (30 packages) |
| `bookings` | User reservations |
| `favorites` | User favorites |
| `reviews` | Ratings and reviews |
| `conversations` | AI chat history |
| `tripadvisor_locations` | Hotels (TripAdvisor) |
| `tripadvisor_photos` | Hotel photos |
| `tripadvisor_reviews` | Hotel reviews |

## Auth (Custom JWT)

- **Service**: `backend/auth/jwt_service.py` (PyJWT + passlib bcrypt)
- **Middleware**: `backend/auth/middleware.py` (get_current_user, get_optional_user)
- Tokens stored in `refresh_tokens` table, rotated on refresh
- Frontend uses `localStorage` for tokens

## Logging

- **Config**: `backend/logging_config.py` (setup_logging() called at FastAPI startup)
- **Output**: `backend/log_apps/` (4 rotating log files, 5 MB max, 3 backups)
- **K8s volume**: hostPath mount from pod `/app/log_apps` to local `backend/log_apps/`
- **Loggers**:
  - `vacanceai` - General app logger (main.py)
  - `database` + `sqlalchemy.engine` - SQL queries logger -> `sql.log`
  - `agents.*` - AI agent loggers (orchestrator, UI, database agents) -> `agents.log`
- All errors from any logger also go to `errors.log`

## AI Agent Architecture

### PageContext System
- `PageContext` React context reports current page data (route, displayed packages/bookings)
- Each page sets its context via `useSetPageContext()` in a useEffect
- `ChatWidget` reads `usePageContext()` and sends it with every WebSocket message
- Backend injects `[Page actuelle: {...}]` into the HumanMessage for the agent
- Agent can resolve "celui-ci", "le premier", "ma derniere reservation" using page context

### Agent Flow
1. User message arrives via WebSocket (`conversations.py`)
2. Orchestrator (`orchestrator/agent.py`) classifies and routes to UI or Database agent
3. UI Agent (`ui/agent.py`) uses Gemini + tools (search, book, navigate, etc.)
4. Tool results with `action` key become UI actions sent back to frontend
5. Frontend `ChatWidget` handles actions (navigate, show cards, etc.)
6. After booking confirmation, ChatWidget auto-navigates to /bookings
7. After adding to favorites, ChatWidget auto-navigates to /favorites

### UI Agent Tools
- `search_vacation` - Search packages with filters
- `show_package_details` - Show package details
- `create_booking_action` - Create a booking directly
- `start_booking_flow` - Open booking form on a package
- `add_to_favorites_action` - Add to favorites
- `navigate_to_page` - Navigate frontend to a page
- `show_recommendations` - Show personalized recommendations

## API Endpoints

### Auth
- `POST /api/auth/signup` - Register
- `POST /api/auth/login` - Login -> access_token + refresh_token
- `POST /api/auth/refresh` - Refresh token
- `POST /api/auth/logout` - Logout
- `GET /api/auth/me` - Profile
- `PATCH /api/auth/me` - Update profile

### Packages
- `GET /api/packages` - List with filters
- `GET /api/packages/featured` - Popular packages
- `GET /api/packages/{id}` - Details

### Bookings
- `GET /api/bookings` - User's bookings
- `POST /api/bookings` - Create booking
- `PATCH /api/bookings/{id}` - Update/cancel

### Favorites
- `GET /api/favorites` - List
- `POST /api/favorites/{package_id}` - Add
- `DELETE /api/favorites/{package_id}` - Remove

### Chat (WebSocket)
- `WS /api/conversations/ws/{id}` - Real-time chat
- `POST /api/conversations/{id}/message` - REST fallback
- `GET /api/conversations/{id}` - History

### TripAdvisor
- `GET /api/tripadvisor/locations` - Hotels
- `GET /api/tripadvisor/locations-with-details` - Hotels with photos + reviews + rating (single query)
- `GET /api/tripadvisor/locations/{id}` - Hotel details + photos + reviews

### Health
- `GET /api/health` - API status
- `GET /api/ready` - Readiness (checks Oracle connection)

## Kubernetes

- **Namespace**: `vacanceai`
- **Deployments**: backend, frontend, jaeger
- **Services**: ClusterIP for all, NodePort for jaeger-external
- **Ingress**: NGINX with WebSocket support (proxy-read-timeout: 3600s)
- **Images**: `vacanceai-backend:latest`, `vacanceai-frontend:latest` (imagePullPolicy: Never)
- **Config**: `k8s/configmap.yaml` (env vars), `k8s/secrets.yaml` (credentials, gitignored)
- **Volumes**: backend has hostPath mount for `log_apps/` (logs visible locally)

## Automated Setup

`setup.ps1` automates the full deployment:
1. Prerequisites check (Docker, kubectl, K8s cluster, .env)
2. Oracle startup (docker compose) + healthcheck
3. Schema initialization (oracle_schema.sql)
4. Docker image builds (backend + frontend)
5. Ingress NGINX Controller installation
6. K8s secrets generation from .env
7. K8s manifest deployment
8. Pod readiness wait

Flags: `-SkipOracle`, `-SkipBuild`, `-SkipSchema`

## Environment Variables

Required in `.env` or `k8s/secrets.yaml`:

```bash
ORACLE_HOST=localhost          # or host.docker.internal in k8s
ORACLE_PORT=1521
ORACLE_SERVICE=XE
ORACLE_USER=VACANCEAI
ORACLE_PASSWORD=vacanceai
JWT_SECRET_KEY=your-secret-key
GOOGLE_API_KEY=your-gemini-api-key
```
