# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

**VacanceAI** is a vacation booking platform with an AI-powered chatbot assistant. The application allows users to browse vacation packages, make bookings, leave reviews, and interact with an intelligent assistant that can help find the perfect vacation.

## Tech Stack

- **Backend**: Python/FastAPI
- **Frontend**: React + TypeScript + Vite
- **Database**: Supabase (PostgreSQL + Auth + Row Level Security)
- **AI**: Google Gemini + pgvector for RAG (Retrieval Augmented Generation)
- **Containerization**: Docker Compose

## Development Commands

```bash
# Start Supabase locally (required first)
npx supabase start

# Start backend + frontend with Docker Compose
docker compose up

# Start in detached mode
docker compose up -d

# Stop all services
docker compose down

# View logs
docker compose logs -f backend
docker compose logs -f frontend

# Run backend locally (without Docker)
cd backend && uvicorn api.main:app --reload --port 8000

# Run frontend locally (without Docker)
cd frontend && npm install && npm run dev
```

### Ports

- **Backend API**: http://localhost:8080
- **Frontend**: http://localhost:5173
- **Supabase Studio**: http://localhost:54323
- **Supabase API**: http://localhost:54321

## Architecture

### Backend Structure

```
backend/
├── api/
│   ├── main.py              # FastAPI app entry point
│   └── routes/
│       ├── auth.py          # Authentication endpoints
│       ├── destinations.py  # Destinations CRUD
│       ├── packages.py      # Vacation packages CRUD
│       ├── bookings.py      # User bookings
│       ├── favorites.py     # User favorites
│       ├── reviews.py       # Package reviews
│       ├── conversations.py # AI chat conversations
│       └── health.py        # Health check
├── agents/                  # A2A Protocol agents
│   ├── base.py              # Base agent class
│   ├── orchestrator/        # Main coordinator agent
│   ├── database/            # Database query agent
│   └── ui/                  # UI automation agent
├── a2a/                     # Agent-to-Agent protocol
│   ├── protocol.py          # Message schemas
│   ├── client.py            # A2A client
│   └── server.py            # A2A server
├── auth/
│   └── middleware.py        # Auth middleware
├── database/
│   └── supabase_client.py   # Supabase client wrapper
└── config.py                # Environment configuration
```

### Frontend Structure

```
frontend/src/
├── components/
│   ├── Layout.tsx           # Main layout wrapper
│   ├── common/
│   │   ├── Header.tsx       # Navigation header
│   │   └── Footer.tsx       # Page footer
│   ├── chat/
│   │   └── ChatWidget.tsx   # AI chatbot widget
│   └── packages/
│       └── PackageCard.tsx  # Package display card
├── pages/
│   ├── Home.tsx             # Landing page
│   ├── Login.tsx            # User login
│   ├── SignUp.tsx           # User registration
│   ├── Search.tsx           # Package search
│   └── Bookings.tsx         # User bookings
├── contexts/
│   └── AuthContext.tsx      # Authentication context
├── services/                # API service calls
├── hooks/                   # Custom React hooks
├── types/                   # TypeScript types
├── App.tsx                  # Main app component
└── main.tsx                 # Entry point
```

### Database Schema (Supabase)

| Table | Description |
|-------|-------------|
| `destinations` | Travel destinations (countries, cities) |
| `packages` | Vacation packages with pricing and availability |
| `bookings` | User reservations |
| `favorites` | User saved packages |
| `reviews` | User reviews and ratings |
| `conversations` | AI chat history |
| `package_embeddings` | Vector embeddings for RAG search |

Row Level Security (RLS) is enabled:
- Destinations & Packages: Public read access
- Bookings, Favorites, Conversations: User owns their data
- Reviews: Public read, authenticated create

## Environment Variables

Required in `.env`:

```bash
# Supabase (from `npx supabase status`)
ANON_KEY=your_anon_key
SERVICE_ROLE_KEY=your_service_role_key

# Google AI
GOOGLE_API_KEY=your_gemini_api_key
```

## Supabase Setup

```bash
# Initialize Supabase (already done)
npx supabase init

# Start local Supabase
npx supabase start

# Apply migrations
npx supabase db reset

# Open Supabase Studio
# http://localhost:54323
```

Migrations are in `supabase/migrations/`.

## API Endpoints

### Auth
- `POST /api/auth/signup` - Register new user
- `POST /api/auth/login` - User login
- `POST /api/auth/logout` - User logout

### Packages
- `GET /api/packages` - List packages
- `GET /api/packages/{id}` - Get package details

### Bookings
- `GET /api/bookings` - User's bookings
- `POST /api/bookings` - Create booking
- `PATCH /api/bookings/{id}` - Update booking

### Favorites
- `GET /api/favorites` - User's favorites
- `POST /api/favorites` - Add favorite
- `DELETE /api/favorites/{id}` - Remove favorite

### Reviews
- `GET /api/reviews` - Package reviews
- `POST /api/reviews` - Create review

### Conversations
- `GET /api/conversations` - User's chat history
- `POST /api/conversations` - Send message to AI

## A2A Protocol

The backend uses an Agent-to-Agent protocol for AI task coordination:

1. **Orchestrator Agent**: Receives user requests and delegates to specialized agents
2. **Database Agent**: Handles Supabase queries and data retrieval
3. **UI Agent**: Manages UI-related tasks and responses

Agents communicate via the protocol defined in `backend/a2a/`.
