# VacanceAI - Vacation Booking Platform

A full-stack vacation booking application with an AI assistant, TripAdvisor integration, and Agent-to-Agent (A2A) protocol.

---

## Overview

**VacanceAI** is a modern vacation booking platform that combines:

- An all-inclusive vacation package catalog
- Real-time hotel data via TripAdvisor
- An intelligent AI assistant (Google Gemini 2.0 Flash)
- An Agent-to-Agent (A2A) architecture for AI orchestration
- Custom JWT authentication with refresh tokens

---

## Tech Stack

| Layer | Technologies |
|-------|-------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Database** | Oracle 21c XE (SQLAlchemy ORM + oracledb) |
| **AI** | Google Gemini 2.0 Flash (LangChain + LangGraph) |
| **Auth** | Custom JWT (PyJWT + passlib bcrypt) |
| **Observability** | OpenTelemetry, Jaeger, LangSmith |
| **AI Studio** | LangGraph Studio (Cloudflare Tunnel) |
| **Logging** | RotatingFileHandler (app, agents, sql, errors) |
| **Containerization** | Docker Compose (DB) + Kubernetes (app) |

---

## Architecture

### Infrastructure

![Infrastructure Diagram](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-083840.png)

> Detailed documentation: [docs/infrastructure.md](docs/infrastructure.md)

### Database

![Class Diagram](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090534.png)

> Detailed documentation: [docs/class-diagram.md](docs/class-diagram.md)

### API Endpoints

![API Endpoints Diagram](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-084040.png)

> Detailed documentation: [docs/api-endpoints.md](docs/api-endpoints.md)

### AI Agent

![AI Agent Diagram](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090149.png)

> Detailed documentation: [docs/agent-ia.md](docs/agent-ia.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Infrastructure](docs/infrastructure.md) | Kubernetes + Docker Compose architecture + communication flows |
| [Database](docs/class-diagram.md) | 11 SQLAlchemy ORM models, relationships, custom Oracle types |
| [API Endpoints](docs/api-endpoints.md) | 40 FastAPI endpoints (9 routers), parameters, auth, response codes |
| [Frontend](docs/frontend.md) | 10 React pages, components, animations, contexts, services |
| [AI Agent and PageContext](docs/agent-ia.md) | LangChain/LangGraph agents, tools, PageContext, WebSocket |
| [A2A Protocol](docs/a2a-protocol.md) | Google Agent-to-Agent, endpoints, communication flow |
| [Installation](docs/installation.md) | Setup, configuration, deployment, commands, logging, troubleshooting |
| [Functional Description](docs/functional-description.md) | 11 user needs (DDD) |
| [Ubiquitous Language](docs/ubiquitous-language.md) | DDD glossary |
| [Domain Model](docs/domain-model.md) | UML class diagram, aggregates, context map |

---

## Quick Start

```powershell
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

# Configure .env (see docs/installation.md)

.\setup.ps1
```

> Full guide: [docs/installation.md](docs/installation.md)

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Swagger | http://localhost/swagger |
| Jaeger UI | http://localhost:31686 |
| LangGraph Studio | https://smith.langchain.com/studio/?baseUrl=\<TUNNEL_URL\> |
| LangSmith | https://smith.langchain.com |

---

## Project Structure

![Project Structure](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-092939.png)

---

## License

MIT

---

## Authors

VacanceAI Team
