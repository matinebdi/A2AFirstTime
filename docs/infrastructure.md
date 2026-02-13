# Infrastructure Diagram - VacanceAI

![Infrastructure Diagram](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-083840.png)

## Description

This diagram represents the VacanceAI infrastructure architecture, composed of two containerization layers: Kubernetes for the application and Docker Compose for the Oracle database.

---

## Components

### Client (React SPA)

The user's browser runs the React application (Single Page Application). It communicates with the backend via HTTP (REST API) and WebSocket (real-time AI chat).

### Kubernetes (namespace: vacanceai)

All application components are deployed in a local Kubernetes cluster (Docker Desktop).

#### Ingress NGINX (localhost:80)

Single entry point that routes traffic:
- `/api/*`, `/swagger`, `/redoc` -> Backend (port 8000)
- `/*` -> Frontend (port 80)
- WebSocket support with `proxy-read-timeout: 3600s` for long-lived chat connections

#### Backend - FastAPI (:8000)

Python FastAPI server with Uvicorn:
- REST API (40 endpoints)
- WebSocket for AI chat
- AI Agents (LangChain + LangGraph)
- JWT authentication
- SQLAlchemy ORM to Oracle
- OpenTelemetry traces to Jaeger
- Rotating logs to hostPath volume

#### Frontend - React + nginx (:80)

React 18 application built and served by nginx:
- SPA with client-side routing
- Tailwind CSS + Framer Motion for animations
- API communication via fetch + WebSocket

#### Jaeger (:16686)

Distributed tracing collector (OpenTelemetry):
- Web interface accessible via NodePort 31686
- Receives traces from the backend for request monitoring

#### log_apps (hostPath volume)

Kubernetes volume mounted from the backend pod to the local filesystem:
- Pod: `/app/log_apps/`
- Local: `backend/log_apps/`
- 4 files: `app.log`, `agents.log`, `sql.log`, `errors.log`
- Automatic rotation (5 MB max, 3 backups)

### Docker Compose

#### Oracle 21c XE (localhost:1521)

Oracle database in a Docker container (separate from Kubernetes):
- `VACANCEAI` schema with 11 tables + triggers
- Persistent volume `oracle-xe-data`
- K8s backend connects via `host.docker.internal:1521`
- Thin oracledb mode (no Oracle Instant Client required)

### Google Gemini 2.0 Flash

External AI service (Google API):
- Used by LangChain/LangGraph agents
- Orchestrator, database agent, and UI agent
- Connection via `GOOGLE_API_KEY`

---

## Communication Flows

| Source | Destination | Protocol | Description |
|--------|-------------|----------|-------------|
| Client | Ingress | HTTP/WS | User requests |
| Ingress | Backend | HTTP/WS | Routing /api/* |
| Ingress | Frontend | HTTP | Routing /* |
| Backend | Oracle | TCP (1521) | SQL queries via SQLAlchemy |
| Backend | Gemini | HTTPS | AI API calls |
| Backend | Jaeger | gRPC/HTTP | Trace export |
| Backend | log_apps | Filesystem | Log writing |
| log_apps | Local | hostPath | K8s volume mount |

---

## Kubernetes Manifests

| File | Resource | Description |
|------|----------|-------------|
| `k8s/namespace.yaml` | Namespace | `vacanceai` |
| `k8s/secrets.yaml` | Secret | Credentials (gitignored) |
| `k8s/configmap.yaml` | ConfigMap | Environment variables |
| `k8s/backend.yaml` | Deployment + Service | FastAPI backend |
| `k8s/frontend.yaml` | Deployment + Service | React/nginx frontend |
| `k8s/jaeger.yaml` | Deployment + Service + NodePort | Jaeger traces |
| `k8s/ingress.yaml` | Ingress | NGINX routing |

---

## Access URLs

| Service | URL | Type |
|---------|-----|------|
| Frontend | http://localhost | Ingress |
| Backend API | http://localhost/api/health | Ingress |
| Swagger | http://localhost/swagger | Ingress |
| ReDoc | http://localhost/redoc | Ingress |
| Jaeger UI | http://localhost:31686 | NodePort |
| Oracle | localhost:1521/XE | Docker Compose |
