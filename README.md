# VacanceAI - Plateforme de Reservation de Vacances

Application complete de reservation de vacances avec assistant IA, integration TripAdvisor et protocole Agent-to-Agent (A2A).

---

## Presentation

**VacanceAI** est une plateforme moderne de reservation de vacances qui combine :

- Un catalogue de packages vacances tout compris
- Des donnees hotels en temps reel via TripAdvisor
- Un assistant IA intelligent (Google Gemini 2.0 Flash)
- Une architecture Agent-to-Agent (A2A) pour l'orchestration IA
- Authentification JWT custom avec refresh tokens

---

## Stack Technique

| Couche | Technologies |
|--------|--------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS, Framer Motion |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Base de donnees** | Oracle 21c XE (SQLAlchemy ORM + oracledb) |
| **IA** | Google Gemini 2.0 Flash (LangChain + LangGraph) |
| **Auth** | JWT custom (PyJWT + passlib bcrypt) |
| **Observabilite** | OpenTelemetry, Jaeger |
| **Logging** | RotatingFileHandler (app, agents, sql, errors) |
| **Conteneurisation** | Docker Compose (DB) + Kubernetes (app) |

---

## Architecture

### Infrastructure

![Diagramme Infrastructure](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-083840.png)

> Documentation detaillee : [docs/infrastructure.md](docs/infrastructure.md)

### Base de donnees

![Diagramme de classes](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090534.png)

> Documentation detaillee : [docs/class-diagram.md](docs/class-diagram.md)

### API Endpoints

![Diagramme API Endpoints](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-084040.png)

> Documentation detaillee : [docs/api-endpoints.md](docs/api-endpoints.md)

### Agent IA

![Diagramme Agent IA](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090149.png)

> Documentation detaillee : [docs/agent-ia.md](docs/agent-ia.md)

---

## Documentation

| Document | Description |
|----------|-------------|
| [Infrastructure](docs/infrastructure.md) | Architecture Kubernetes + Docker Compose + flux de communication |
| [Base de donnees](docs/class-diagram.md) | 11 modeles SQLAlchemy ORM, relations, types custom Oracle |
| [API Endpoints](docs/api-endpoints.md) | 40 endpoints FastAPI (9 routers), parametres, auth, codes de reponse |
| [Frontend](docs/frontend.md) | 10 pages React, composants, animations, contexts, services |
| [Agent IA et PageContext](docs/agent-ia.md) | Agents LangChain/LangGraph, outils, PageContext, WebSocket |
| [Protocole A2A](docs/a2a-protocol.md) | Agent-to-Agent de Google, endpoints, flux de communication |
| [Installation](docs/installation.md) | Setup, configuration, lancement, commandes, logging, troubleshooting |
| [Description fonctionnelle](docs/functional-description.md) | 11 besoins utilisateur (DDD) |
| [Langage ubiquitaire](docs/ubiquitous-language.md) | Glossaire DDD |
| [Modele de domaine](docs/domain-model.md) | Diagramme UML Mermaid, aggregats, context map |

---

## Demarrage rapide

```powershell
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

# Configurer .env (voir docs/installation.md)

.\setup.ps1
```

> Guide complet : [docs/installation.md](docs/installation.md)

### URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| Swagger | http://localhost/swagger |
| Jaeger UI | http://localhost:31686 |

---

## Structure du projet

```
ui-automation-a2a/
├── backend/
│   ├── api/                        # FastAPI (main.py + 9 routers)
│   ├── agents/                     # IA (orchestrator, database, ui)
│   ├── a2a/                        # Protocole Agent-to-Agent
│   ├── auth/                       # JWT service + middleware
│   ├── database/                   # SQLAlchemy ORM (models, session, schema)
│   ├── logging_config.py
│   ├── log_apps/                   # Logs (montes via K8s hostPath)
│   ├── config.py
│   ├── telemetry.py
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/             # Layout, animations, chat, search, packages
│   │   ├── pages/                  # 10 pages
│   │   ├── contexts/               # AuthContext + PageContext
│   │   ├── hooks/                  # useChat (WebSocket)
│   │   └── services/               # API clients
│   └── Dockerfile.prod
│
├── scripts/seed_oracle.py          # Seed donnees
├── k8s/                            # Manifestes Kubernetes
├── docs/                           # Documentation complete
├── setup.ps1                       # Setup automatique
├── compose.yaml                    # Docker Compose (Oracle)
└── README.md
```

---

## Licence

MIT

---

## Auteurs

VacanceAI Team
