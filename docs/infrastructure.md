# Diagramme d'Infrastructure - VacanceAI

![Diagramme Infrastructure](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-083840.png)

## Description

Ce diagramme represente l'architecture d'infrastructure de VacanceAI, composee de deux couches de conteneurisation : Kubernetes pour l'application et Docker Compose pour la base de donnees Oracle.

---

## Composants

### Client (React SPA)

Le navigateur de l'utilisateur execute l'application React (Single Page Application). Il communique avec le backend via HTTP (API REST) et WebSocket (chat IA en temps reel).

### Kubernetes (namespace: vacanceai)

Tous les composants applicatifs sont deployes dans un cluster Kubernetes local (Docker Desktop).

#### Ingress NGINX (localhost:80)

Point d'entree unique qui route le trafic :
- `/api/*`, `/swagger`, `/redoc` -> Backend (port 8000)
- `/*` -> Frontend (port 80)
- Support WebSocket avec `proxy-read-timeout: 3600s` pour les connexions chat longues

#### Backend - FastAPI (:8000)

Serveur Python FastAPI avec Uvicorn :
- API REST (40 endpoints)
- WebSocket pour le chat IA
- Agents IA (LangChain + LangGraph)
- Authentification JWT
- ORM SQLAlchemy vers Oracle
- Traces OpenTelemetry vers Jaeger
- Logs rotatifs vers le volume hostPath

#### Frontend - React + nginx (:80)

Application React 18 buildee et servie par nginx :
- SPA avec routing cote client
- Tailwind CSS + Framer Motion pour les animations
- Communication API via fetch + WebSocket

#### Jaeger (:16686)

Collecteur de traces distribuees (OpenTelemetry) :
- Interface web accessible via NodePort 31686
- Recoit les traces du backend pour le monitoring des requetes

#### log_apps (hostPath volume)

Volume Kubernetes monte depuis le pod backend vers le systeme de fichiers local :
- Pod : `/app/log_apps/`
- Local : `backend/log_apps/`
- 4 fichiers : `app.log`, `agents.log`, `sql.log`, `errors.log`
- Rotation automatique (5 MB max, 3 backups)

### Docker Compose

#### Oracle 21c XE (localhost:1521)

Base de donnees Oracle en conteneur Docker (separee de Kubernetes) :
- Schema `VACANCEAI` avec 11 tables + triggers
- Volume persistant `oracle-xe-data`
- Le backend K8s se connecte via `host.docker.internal:1521`
- Mode thin oracledb (pas d'Oracle Instant Client requis)

### Google Gemini 2.0 Flash

Service IA externe (API Google) :
- Utilise par les agents LangChain/LangGraph
- Orchestrateur, agent database et agent UI
- Connexion via `GOOGLE_API_KEY`

---

## Flux de communication

| Source | Destination | Protocole | Description |
|--------|-------------|-----------|-------------|
| Client | Ingress | HTTP/WS | Requetes utilisateur |
| Ingress | Backend | HTTP/WS | Routage /api/* |
| Ingress | Frontend | HTTP | Routage /* |
| Backend | Oracle | TCP (1521) | Requetes SQL via SQLAlchemy |
| Backend | Gemini | HTTPS | Appels API IA |
| Backend | Jaeger | gRPC/HTTP | Envoi de traces |
| Backend | log_apps | Filesystem | Ecriture des logs |
| log_apps | Local | hostPath | Montage volume K8s |

---

## Manifestes Kubernetes

| Fichier | Ressource | Description |
|---------|-----------|-------------|
| `k8s/namespace.yaml` | Namespace | `vacanceai` |
| `k8s/secrets.yaml` | Secret | Credentials (gitignored) |
| `k8s/configmap.yaml` | ConfigMap | Variables d'environnement |
| `k8s/backend.yaml` | Deployment + Service | Backend FastAPI |
| `k8s/frontend.yaml` | Deployment + Service | Frontend React/nginx |
| `k8s/jaeger.yaml` | Deployment + Service + NodePort | Jaeger traces |
| `k8s/ingress.yaml` | Ingress | Routage NGINX |

---

## URLs d'acces

| Service | URL | Type |
|---------|-----|------|
| Frontend | http://localhost | Ingress |
| API Backend | http://localhost/api/health | Ingress |
| Swagger | http://localhost/swagger | Ingress |
| ReDoc | http://localhost/redoc | Ingress |
| Jaeger UI | http://localhost:31686 | NodePort |
| Oracle | localhost:1521/XE | Docker Compose |
