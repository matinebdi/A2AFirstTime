# VacanceAI - Plateforme de Reservation de Vacances

Application complete de reservation de vacances avec assistant IA, integration TripAdvisor et protocole Agent-to-Agent (A2A).

---

## Table des matieres

1. [Presentation](#presentation)
2. [Fonctionnalites](#fonctionnalites)
3. [Stack Technique](#stack-technique)
4. [Architecture](#architecture)
5. [Base de donnees](#base-de-donnees)
6. [API Backend](#api-backend)
7. [Frontend](#frontend)
8. [Agent IA et PageContext](#agent-ia-et-pagecontext)
9. [Protocole A2A](#protocole-a2a)
10. [Installation](#installation)
11. [Configuration](#configuration)
12. [Lancement](#lancement)
13. [Commandes utiles](#commandes-utiles)
14. [Logging](#logging)
15. [Developpement local](#developpement-local)
16. [Troubleshooting](#troubleshooting)

---

## Presentation

**VacanceAI** est une plateforme moderne de reservation de vacances qui combine :

- Un catalogue de packages vacances tout compris
- Des donnees hotels en temps reel via TripAdvisor
- Un assistant IA intelligent (Google Gemini)
- Une architecture Agent-to-Agent (A2A) pour l'orchestration IA
- Authentification JWT custom avec refresh tokens

---

## Fonctionnalites

### Pour les utilisateurs
- Recherche de packages vacances avec filtres (prix, duree, destination)
- Consultation des hotels TripAdvisor avec photos et avis
- Reservation en ligne (directe ou via chatbot IA)
- Gestion des favoris
- Historique des reservations (AG Grid avec tri/filtre/pagination)
- Chat avec assistant IA context-aware (connait la page courante)

### Pour les developpeurs
- API REST complete (40 endpoints) + WebSocket pour le chat en temps reel
- Protocole A2A pour communication inter-agents
- Base de donnees Oracle 21c XE avec ORM SQLAlchemy
- Observabilite avec OpenTelemetry + Jaeger
- Logging centralise (4 fichiers rotatifs)
- PageContext system : l'agent IA connait la page et les donnees affichees

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

![Diagramme Infrastructure](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-081923.png)

> Documentation detaillee : [docs/infrastructure.md](docs/infrastructure.md)

```
                    Kubernetes (namespace: vacanceai)
  ┌──────────────────────────────────────────────────────────┐
  │                                                          │
  │   ┌─────────────┐    Ingress NGINX (localhost:80)        │
  │   │   Ingress   │──── /api, /swagger ──► backend:8000   │
  │   │   NGINX     │──── / ──────────────► frontend:80     │
  │   └─────────────┘                                        │
  │                                                          │
  │   ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  │
  │   │   Backend    │  │   Frontend   │  │    Jaeger    │  │
  │   │   FastAPI    │  │  React/nginx │  │   Traces     │  │
  │   │   :8000      │  │   :80        │  │   :16686     │  │
  │   └──────┬───────┘  └──────────────┘  └──────────────┘  │
  │          │ SQLAlchemy ORM + oracledb (thin)               │
  │          │ log_apps/ (hostPath volume -> repo local)     │
  └──────────┼───────────────────────────────────────────────┘
             │ host.docker.internal:1521
  ┌──────────▼───────────────────────────────────────────────┐
  │              Docker Compose                               │
  │   ┌──────────────────────────────────────┐               │
  │   │          Oracle 21c XE               │               │
  │   │   Schema VACANCEAI (11 tables)       │               │
  │   │   localhost:1521                     │               │
  │   └──────────────────────────────────────┘               │
  └──────────────────────────────────────────────────────────┘
```

### Structure des dossiers

```
ui-automation-a2a/
├── backend/
│   ├── api/
│   │   ├── main.py                 # Point d'entree FastAPI
│   │   └── routes/                 # 9 routers (40 endpoints)
│   ├── agents/
│   │   ├── base.py                 # Config LLM (Gemini)
│   │   ├── orchestrator/           # Agent coordinateur
│   │   ├── database/               # Agent requetes DB
│   │   └── ui/                     # Agent UI
│   ├── a2a/                        # Protocole Agent-to-Agent
│   ├── auth/                       # JWT service + middleware
│   ├── database/
│   │   ├── models.py               # 11 modeles SQLAlchemy ORM
│   │   ├── session.py              # Engine + SessionLocal + get_db
│   │   ├── types.py                # Types custom (JSONEncodedCLOB, OracleBoolean)
│   │   └── oracle_schema.sql       # Schema complet (11 tables + triggers)
│   ├── logging_config.py           # Logging centralise
│   ├── log_apps/                   # Fichiers logs (montes via K8s hostPath)
│   ├── config.py                   # Configuration (pydantic-settings)
│   ├── telemetry.py                # OpenTelemetry setup
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── animations/         # Framer Motion (FadeIn, HeroCarousel, etc.)
│   │   │   ├── chat/ChatWidget.tsx  # Chat flottant (WebSocket + PageContext)
│   │   │   ├── search/             # Filtres (DualRangeSlider, TagFilter, etc.)
│   │   │   └── packages/PackageCard.tsx
│   │   ├── pages/                  # 10 pages (Home, Search, Hotels, etc.)
│   │   ├── contexts/               # AuthContext + PageContext
│   │   ├── hooks/useChat.ts        # WebSocket chat hook
│   │   ├── services/               # API clients
│   │   └── types/
│   ├── Dockerfile.prod             # Prod (nginx)
│   └── nginx.conf
│
├── scripts/
│   └── seed_oracle.py              # Seed donnees Oracle + TripAdvisor
│
├── k8s/                            # Manifestes Kubernetes
│
├── docs/                           # Documentation
│   ├── class-diagram.md            # Diagramme de classes ORM
│   ├── api-endpoints.md            # Diagramme des API endpoints
│   ├── infrastructure.md           # Diagramme d'infrastructure
│   ├── functional-description.md   # Description fonctionnelle (DDD)
│   ├── ubiquitous-language.md      # Langage ubiquitaire (DDD)
│   ├── domain-model.md             # Modele de domaine (DDD)
│   └── sc/                         # Screenshots des diagrammes
│
├── setup.ps1                       # Setup automatique
├── .env                            # Variables d'environnement
├── compose.yaml                    # Docker Compose (Oracle)
└── README.md
```

---

## Base de donnees

![Diagramme de classes](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074224.png)

> Documentation detaillee : [docs/class-diagram.md](docs/class-diagram.md)

### Oracle 21c XE

- **User** : `VACANCEAI` / `vacanceai`
- **Schema** : `backend/database/oracle_schema.sql` (11 tables + triggers)
- **ORM** : SQLAlchemy 2.0+ avec `oracledb` en mode thin (pas d'Oracle Instant Client requis)
- **Modeles** : `backend/database/models.py` (11 modeles avec relationships et methodes `to_dict()`)
- **Session** : `backend/database/session.py` (engine, `get_db` dependency, `create_session` pour WebSocket/agents)

### Tables

| Table | Description |
|-------|-------------|
| `users` | Utilisateurs |
| `refresh_tokens` | Tokens JWT de refresh |
| `destinations` | Destinations (15 pays) |
| `packages` | Packages vacances (30 packages) |
| `bookings` | Reservations |
| `favorites` | Favoris utilisateurs |
| `reviews` | Avis et notes |
| `conversations` | Historique chat IA |
| `tripadvisor_locations` | Hotels TripAdvisor |
| `tripadvisor_photos` | Photos TripAdvisor |
| `tripadvisor_reviews` | Avis TripAdvisor |

### Conventions Oracle

| PostgreSQL (ancien) | Oracle (actuel) |
|---------------------|-----------------|
| `BOOLEAN` | `NUMBER(1)` via `OracleBoolean` |
| `UUID` | `VARCHAR2(36)` + `SYS_GUID()` |
| `JSONB` | `CLOB` via `JSONEncodedCLOB` |
| `TEXT[]` | `CLOB` (JSON array) |
| `SERIAL` | Triggers + sequences |
| Raw SQL | SQLAlchemy ORM |

---

## API Backend

![Diagramme API Endpoints](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074628.png)

> Documentation detaillee : [docs/api-endpoints.md](docs/api-endpoints.md)

### Authentification (JWT)

```
POST  /api/auth/signup              # Inscription
POST  /api/auth/login               # Connexion -> access_token + refresh_token
POST  /api/auth/refresh             # Renouveler le token
POST  /api/auth/logout              # Deconnexion
GET   /api/auth/me                  # Profil utilisateur
PATCH /api/auth/me                  # Modifier le profil
POST  /api/auth/avatar              # Upload avatar
GET   /api/auth/avatar/{filename}   # Telecharger avatar
```

### Packages

```
GET  /api/packages                    # Liste avec filtres (prix, duree, tags, tri)
GET  /api/packages/featured           # Packages populaires
GET  /api/packages/{id}               # Details + destination + avis
GET  /api/packages/{id}/availability  # Verification de disponibilite
```

### Reservations

```
GET    /api/bookings           # Mes reservations
POST   /api/bookings           # Creer une reservation
GET    /api/bookings/{id}      # Details
PATCH  /api/bookings/{id}      # Modifier (statut, demandes)
DELETE /api/bookings/{id}      # Supprimer
```

### Favoris

```
GET    /api/favorites                    # Mes favoris
POST   /api/favorites/{package_id}       # Ajouter
DELETE /api/favorites/{package_id}       # Supprimer
GET    /api/favorites/check/{package_id} # Verifier si favori
```

### Avis

```
GET  /api/reviews/package/{package_id}  # Avis d'un package
POST /api/reviews                       # Publier un avis (1-5)
```

### Destinations

```
GET /api/destinations                    # Liste (filtres: country, tags)
GET /api/destinations/{id}               # Details + packages
GET /api/destinations/{id}/packages      # Packages d'une destination
```

### Chat IA

```
WS   /api/conversations/ws/{id}          # WebSocket temps reel
POST /api/conversations/new              # Nouvelle conversation
GET  /api/conversations/{id}             # Historique
POST /api/conversations/{id}/message     # Envoyer message (fallback REST)
DELETE /api/conversations/{id}           # Supprimer
```

### TripAdvisor

```
GET /api/tripadvisor/locations                # Hotels
GET /api/tripadvisor/locations-with-details   # Hotels + photos + avis (optimise)
GET /api/tripadvisor/countries                # Pays disponibles
GET /api/tripadvisor/locations/{id}           # Details hotel
GET /api/tripadvisor/locations/{id}/photos    # Photos
GET /api/tripadvisor/locations/{id}/reviews   # Avis
```

### Health

```
GET /api/health    # Liveness probe
GET /api/ready     # Readiness probe (verifie Oracle)
```

---

## Frontend

### Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Accueil avec hero carousel + packages populaires |
| `/search` | Search | Recherche avec filtres (prix, duree, tags, pagination) |
| `/packages/:id` | PackageDetail | Details d'un package + formulaire reservation |
| `/hotels` | Hotels | Hotels TripAdvisor (grille 3 colonnes, tilt 3D) |
| `/hotels/:locationId` | HotelDetail | Details hotel + photos + avis progressifs |
| `/favorites` | Favorites | Mes favoris |
| `/bookings` | Bookings | Mes reservations (AG Grid) |
| `/profile` | Profile | Profil utilisateur + upload avatar |
| `/login` | Login | Connexion |
| `/signup` | SignUp | Inscription |

### Composants principaux

- **Layout** : AnimatedBackground + Header (glass effect) + AnimatePresence + Footer
- **ChatWidget** : Widget de chat flottant (WebSocket + PageContext)
- **PackageCard** : Carte avec effet tilt 3D (react-parallax-tilt)
- **HeroCarousel** : Carousel Ken Burns (crossfade, zoom/pan)
- **Animations** : FadeIn, StaggerContainer, PageTransition, AnimatedButton

---

## Agent IA et PageContext

L'agent IA connait la page que l'utilisateur consulte et les donnees affichees. Cela permet des interactions comme "reserve celui-ci" ou "montre-moi le premier" sans ambiguite.

### Fonctionnement

1. **`PageContext`** (React Context) stocke les infos de la page courante
2. Chaque page met a jour ce contexte via `useSetPageContext()`
3. **`ChatWidget`** lit `usePageContext()` et l'envoie avec chaque message WebSocket
4. Le backend injecte `[Page actuelle: {...}]` dans le message pour l'agent Gemini
5. L'agent utilise ces donnees pour resoudre les references implicites

### Donnees envoyees par page

| Page | Donnees |
|------|---------|
| Home | `featured_packages: [{id, name}]` |
| Search | `filters: {destination, min_price, ...}`, `results: [{id, name, price}]` |
| PackageDetail | `package_id, package_name, destination, price, duration` |
| Bookings | `bookings: [{id, package_name, status, start_date}]` |
| Hotels | `hotels: [{location_id, name, country, rating}]` |
| HotelDetail | `location_id, hotel_name, country, rating` |

### Outils de l'agent UI

| Outil | Description |
|-------|-------------|
| `search_vacation` | Rechercher des packages avec filtres |
| `show_package_details` | Afficher les details d'un package |
| `create_booking_action` | Creer une reservation directement |
| `start_booking_flow` | Ouvrir le formulaire de reservation |
| `add_to_favorites_action` | Ajouter aux favoris |
| `navigate_to_page` | Naviguer vers une page |
| `show_recommendations` | Afficher des recommandations |

### Navigation automatique apres action

| Action agent | Navigation |
|-------------|------------|
| Reservation confirmee (`booking_confirmed`) | `/bookings` |
| Ajout aux favoris (`add_favorite`) | `/favorites` |

---

## Protocole A2A

Le backend utilise le protocole Agent-to-Agent (A2A) de Google pour la coordination des agents IA.

### Agents

| Agent | Description |
|-------|-------------|
| **Orchestrator** | Coordonne les autres agents (LangGraph) |
| **Database** | Requetes Oracle (LangChain tools) |
| **UI** | Actions interface utilisateur (ReAct) |

### Endpoints A2A

```
GET  /.well-known/agent.json    # Agent Card (metadonnees)
POST /a2a/tasks                  # Creer une tache
GET  /a2a/tasks/{id}            # Status d'une tache
POST /a2a/tasks/{id}/messages   # Envoyer un message
POST /a2a/tasks/{id}/cancel     # Annuler une tache
```

---

## Installation

### Prerequis

- **Docker Desktop** (v24+) avec **Kubernetes active** (Settings > Kubernetes > Enable)
- **kubectl** (inclus avec Docker Desktop)
- **Git**
- **Python 3.12+** (pour le script de seed)

### Option A : Setup automatique (recommande)

```powershell
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

# Configurer .env (voir section Configuration)

.\setup.ps1
```

Le script `setup.ps1` execute automatiquement :
1. Verification des prerequis (Docker, kubectl, K8s, .env)
2. Demarrage Oracle (docker compose) + healthcheck
3. Initialisation du schema Oracle
4. Build des images Docker (backend + frontend)
5. Installation Ingress NGINX Controller
6. Generation des secrets K8s depuis .env
7. Deploiement des manifests Kubernetes
8. Attente que les pods soient Ready

Flags optionnels : `-SkipOracle`, `-SkipBuild`, `-SkipSchema`

### Option B : Setup manuel

```bash
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

---

## Configuration

### Variables d'environnement (.env)

Creer un fichier `.env` a la racine du projet :

```env
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XE
ORACLE_USER=VACANCEAI
ORACLE_PASSWORD=vacanceai

JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

GOOGLE_API_KEY=<votre_cle_gemini>
```

### Secrets Kubernetes (k8s/secrets.yaml)

Encoder vos valeurs en base64 et les mettre dans `k8s/secrets.yaml` :

```bash
echo -n "votre-valeur" | base64
```

Secrets requis : `ORACLE_PWD`, `ORACLE_PASSWORD`, `JWT_SECRET_KEY`, `GOOGLE_API_KEY`

---

## Lancement

### 1. Demarrer Oracle (Docker Compose)

```bash
docker compose up -d
```

Attendre qu'Oracle soit healthy (~2 minutes au premier lancement) :

```bash
docker compose ps   # oracle-xe doit etre "healthy"
```

### 2. Initialiser le schema Oracle

```bash
docker exec -i oracle-xe sqlplus SYS/admin@//localhost:1521/XE as SYSDBA < backend/database/oracle_schema.sql
```

### 3. Seed les donnees

```bash
pip install oracledb requests
python scripts/seed_oracle.py
```

Cela insere :
- 15 destinations (15 pays)
- 30 packages (2 par pays : Explorer + Premium)
- 150 hotels TripAdvisor avec photos et avis

### 4. Builder les images Docker

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
```

### 5. Deployer sur Kubernetes

```bash
kubectl apply -f k8s/
```

### 6. Verifier le deploiement

```bash
kubectl get pods -n vacanceai

# Resultat attendu :
# NAME                        READY   STATUS    AGE
# backend-xxx                 1/1     Running   ...
# frontend-xxx                1/1     Running   ...
# jaeger-xxx                  1/1     Running   ...
```

### URLs disponibles

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API | http://localhost/api/health |
| Swagger | http://localhost/swagger |
| ReDoc | http://localhost/redoc |
| Jaeger UI | http://localhost:31686 |
| Oracle | localhost:1521/XE |

---

## Commandes utiles

### Docker Compose (Oracle)

```bash
docker compose up -d          # Demarrer Oracle
docker compose down            # Arreter Oracle
docker compose logs -f oracle  # Logs Oracle
```

### Kubernetes (App)

```bash
kubectl get pods -n vacanceai                        # Etat des pods
kubectl logs -n vacanceai deploy/backend -f          # Logs backend
kubectl logs -n vacanceai deploy/frontend -f         # Logs frontend

# Rebuild + redemarrer
docker build -t vacanceai-backend ./backend
kubectl rollout restart deploy/backend -n vacanceai

# Sante
curl http://localhost/api/health
curl http://localhost/api/ready

# Tout supprimer
kubectl delete -f k8s/
```

---

## Logging

Le backend dispose d'un systeme de logging centralise qui ecrit dans `backend/log_apps/`.

| Fichier | Contenu | Niveau |
|---------|---------|--------|
| `app.log` | Logs generaux de l'application | INFO+ |
| `agents.log` | Activite des agents IA (orchestrateur, UI, database) | DEBUG+ |
| `sql.log` | Toutes les requetes SQL | DEBUG+ |
| `errors.log` | Erreurs de tous les loggers | ERROR+ |

- **Rotation** : 5 MB max par fichier, 3 backups
- **Volume K8s** : hostPath monte depuis le pod vers `backend/log_apps/` local

```bash
cat backend/log_apps/app.log      # Logs generaux
cat backend/log_apps/sql.log      # Requetes SQL
cat backend/log_apps/agents.log   # Agents IA
cat backend/log_apps/errors.log   # Erreurs
```

---

## Developpement local

### Backend (sans Docker/K8s)

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Oracle doit tourner sur localhost:1521
uvicorn api.main:app --reload --port 8000
```

### Frontend (sans Docker/K8s)

```bash
cd frontend
npm install
npm run dev
# Ouvre http://localhost:5173
```

---

## Troubleshooting

### Backend ne demarre pas (readiness 503)

Le readiness probe verifie la connexion Oracle. Verifier qu'Oracle tourne :

```bash
docker compose ps   # oracle-xe doit etre "healthy"
```

### ErrImageNeverPull dans K8s

Les images Docker n'existent pas localement. Builder d'abord :

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
kubectl rollout restart deploy/backend deploy/frontend -n vacanceai
```

### Reset complet

```bash
kubectl delete -f k8s/
docker compose down
docker volume create oracle-xe-data
docker compose up -d
# Attendre healthy, puis re-seed et re-deployer
```

---

## Licence

MIT

---

## Auteurs

VacanceAI Team
