# VacanceAI - Plateforme de Reservation de Vacances

Application complete de reservation de vacances avec assistant IA, integration TripAdvisor et protocole Agent-to-Agent (A2A).

---

## Table des matieres

1. [Presentation](#presentation)
2. [Fonctionnalites](#fonctionnalites)
3. [Stack Technique](#stack-technique)
4. [Architecture](#architecture)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Lancement](#lancement)
8. [Base de donnees](#base-de-donnees)
9. [API Backend](#api-backend)
10. [Frontend](#frontend)
11. [Import TripAdvisor](#import-tripadvisor)
12. [Protocole A2A](#protocole-a2a)
13. [Developpement](#developpement)

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
- API REST complete + WebSocket pour le chat en temps reel
- Protocole A2A pour communication inter-agents
- Base de donnees Oracle 21c XE
- Observabilite avec OpenTelemetry + Jaeger
- PageContext system : l'agent IA connait la page et les donnees affichees

---

## Stack Technique

| Couche | Technologies |
|--------|--------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Base de donnees** | Oracle 21c XE (SQLAlchemy ORM + oracledb) |
| **IA** | Google Gemini (LangChain + LangGraph) |
| **Auth** | JWT custom (PyJWT + passlib bcrypt) |
| **Observabilite** | OpenTelemetry, Jaeger |
| **Logging** | RotatingFileHandler (app, agents, sql, errors) |
| **Conteneurisation** | Docker Compose (DB) + Kubernetes (app) |

---

## Architecture

### Diagramme de classes (modeles ORM)

Les 11 modeles SQLAlchemy et leurs relations ([documentation detaillee](docs/class-diagram.md)) :

![Diagramme de classes](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074224.png)

### Diagramme des API Endpoints

Les 40 endpoints FastAPI organises en 9 routers ([documentation detaillee](docs/api-endpoints.md)) :

![Diagramme API Endpoints](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074628.png)

### Infrastructure

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
│   │   └── routes/
│   │       ├── auth.py             # Authentification (JWT)
│   │       ├── packages.py         # Packages vacances
│   │       ├── bookings.py         # Reservations
│   │       ├── favorites.py        # Favoris
│   │       ├── reviews.py          # Avis
│   │       ├── destinations.py     # Destinations
│   │       ├── conversations.py    # Chat IA
│   │       ├── tripadvisor.py      # Donnees TripAdvisor
│   │       └── health.py           # Health + Readiness
│   ├── agents/
│   │   ├── base.py                 # Config LLM (Gemini)
│   │   ├── orchestrator/           # Agent coordinateur
│   │   ├── database/               # Agent requetes DB
│   │   └── ui/                     # Agent UI
│   ├── a2a/
│   │   ├── protocol.py             # Schemas A2A
│   │   ├── client.py               # Client A2A
│   │   └── server.py               # Serveur A2A
│   ├── auth/
│   │   ├── jwt_service.py          # Service JWT (PyJWT + bcrypt)
│   │   └── middleware.py           # Middleware auth
│   ├── database/
│   │   ├── models.py               # Modeles SQLAlchemy ORM (11 modeles)
│   │   ├── session.py              # Engine + SessionLocal + get_db
│   │   ├── types.py                # Types custom (JSONEncodedCLOB, OracleBoolean)
│   │   └── oracle_schema.sql       # Schema complet (11 tables)
│   ├── logging_config.py           # Logging centralise (RotatingFileHandler -> log_apps/)
│   ├── log_apps/                   # Fichiers logs (montes via volume K8s hostPath)
│   │   ├── app.log                 # Logs generaux (INFO+)
│   │   ├── agents.log              # Activite agents IA (DEBUG+)
│   │   ├── sql.log                 # Requetes SQL (DEBUG+)
│   │   └── errors.log              # Erreurs uniquement (ERROR+)
│   ├── config.py                   # Configuration (pydantic-settings)
│   ├── telemetry.py                # OpenTelemetry setup
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── chat/ChatWidget.tsx    # Chat flottant (WebSocket + PageContext)
│   │   │   └── packages/PackageCard.tsx
│   │   ├── pages/
│   │   │   ├── Home.tsx              # + PageContext: featured packages
│   │   │   ├── Search.tsx            # + PageContext: filtres + resultats
│   │   │   ├── PackageDetail.tsx     # + PageContext: package affiche
│   │   │   ├── Bookings.tsx          # + PageContext: liste reservations
│   │   │   ├── Hotels.tsx            # + PageContext: liste hotels
│   │   │   └── HotelDetail.tsx       # + PageContext: hotel affiche
│   │   ├── contexts/
│   │   │   ├── AuthContext.tsx        # Auth JWT (localStorage)
│   │   │   └── PageContext.tsx        # Contexte page courante pour agent IA
│   │   ├── hooks/useChat.ts           # WebSocket chat hook
│   │   ├── services/
│   │   ├── types/
│   │   ├── App.tsx
│   │   └── main.tsx
│   ├── Dockerfile                  # Dev (Vite)
│   ├── Dockerfile.prod             # Prod (nginx)
│   └── nginx.conf
│
├── scripts/
│   └── seed_oracle.py              # Seed donnees Oracle + TripAdvisor
│
├── k8s/                            # Manifestes Kubernetes
│   ├── namespace.yaml
│   ├── secrets.yaml                # (gitignored)
│   ├── configmap.yaml
│   ├── jaeger.yaml
│   ├── backend.yaml
│   ├── frontend.yaml
│   └── ingress.yaml
│
├── docs/                           # Documentation DDD
│   ├── class-diagram.md            # Diagramme de classes ORM
│   ├── api-endpoints.md            # Diagramme des API endpoints
│   ├── functional-description.md   # Description fonctionnelle
│   ├── ubiquitous-language.md      # Langage ubiquitaire
│   ├── domain-model.md             # Modele de domaine (UML Mermaid)
│   └── sc/                         # Screenshots des diagrammes Mermaid
│
├── setup.ps1                       # Setup automatique (Oracle + build + K8s)
├── .env                            # Variables d'environnement
├── compose.yaml                    # Docker Compose (Oracle uniquement)
└── README.md
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
# Cloner le repo
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime

# Creer le volume Oracle
docker volume create oracle-xe-data

# Configurer .env (voir section Configuration)

# Lancer le setup complet
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

#### Etape 1 : Cloner le repository

```bash
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
```

#### Etape 2 : Creer le volume Oracle

```bash
docker volume create oracle-xe-data
```

#### Etape 3 : Installer l'Ingress NGINX Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml

# Attendre qu'il soit pret
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

Les secrets requis :
- `ORACLE_PWD` : mot de passe SYS Oracle (default: `admin`)
- `ORACLE_PASSWORD` : mot de passe user VACANCEAI (default: `vacanceai`)
- `JWT_SECRET_KEY` : cle secrete JWT
- `GOOGLE_API_KEY` : cle API Google Gemini

---

## Lancement

### 1. Demarrer Oracle (Docker Compose)

```bash
docker compose up -d
```

Attendre qu'Oracle soit healthy (~2 minutes au premier lancement) :

```bash
docker compose ps
# oracle-xe   Up (healthy)
```

### 2. Initialiser le schema Oracle

```bash
docker exec -i oracle-xe bash -c "echo -e '@/tmp/schema.sql\nexit;' | sqlplus -s / as sysdba"
# Ou :
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
# Backend
docker build -t vacanceai-backend ./backend

# Frontend (production avec nginx)
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
```

### 5. Deployer sur Kubernetes

```bash
kubectl apply -f k8s/
```

Ou etape par etape :

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
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
# Etat des pods
kubectl get pods -n vacanceai

# Logs
kubectl logs -n vacanceai deploy/backend -f
kubectl logs -n vacanceai deploy/frontend -f

# Redemarrer apres un rebuild d'image
docker build -t vacanceai-backend ./backend
kubectl rollout restart deploy/backend -n vacanceai

# Sante
curl http://localhost/api/health
curl http://localhost/api/ready

# Tout supprimer
kubectl delete -f k8s/
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

### Conventions Oracle

| PostgreSQL (ancien) | Oracle (actuel) |
|---------------------|-----------------|
| `BOOLEAN` | `NUMBER(1)` |
| `UUID` | `VARCHAR2(36)` + `SYS_GUID()` |
| `JSONB` | `CLOB` avec contrainte `IS JSON` |
| `TEXT[]` | `CLOB` (JSON array) |
| `SERIAL` | Triggers + sequences |
| `LIMIT/OFFSET` | SQLAlchemy `.offset()` / `.limit()` |
| Raw SQL | SQLAlchemy ORM (`db.query(Model).filter(...)`) |

### Tables

| Table | Description |
|-------|-------------|
| `users` | Utilisateurs |
| `refresh_tokens` | Tokens JWT de refresh |
| `destinations` | Destinations (15 pays) |
| `packages` | Packages vacances |
| `bookings` | Reservations |
| `favorites` | Favoris utilisateurs |
| `reviews` | Avis et notes |
| `conversations` | Historique chat IA |
| `tripadvisor_locations` | Hotels TripAdvisor |
| `tripadvisor_photos` | Photos TripAdvisor |
| `tripadvisor_reviews` | Avis TripAdvisor |

---

## API Backend

![Diagramme API Endpoints](docs/sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074628.png)

> Documentation detaillee : [docs/api-endpoints.md](docs/api-endpoints.md)

### Authentification (JWT)

```
POST  /api/auth/signup          # Inscription
POST  /api/auth/login           # Connexion -> access_token + refresh_token
POST  /api/auth/refresh         # Renouveler le token
POST  /api/auth/logout          # Deconnexion
GET   /api/auth/me              # Profil utilisateur
PATCH /api/auth/me              # Modifier le profil
```

### Destinations

```
GET /api/destinations
GET /api/destinations/{id}
```

### Packages

```
GET  /api/packages                    # Liste avec filtres
GET  /api/packages/featured           # Packages populaires
GET  /api/packages/{id}               # Details
GET  /api/packages/{id}/availability  # Disponibilite
```

### Reservations

```
GET   /api/bookings           # Mes reservations
GET   /api/bookings/{id}      # Details
POST  /api/bookings           # Creer
PATCH /api/bookings/{id}      # Modifier
DELETE /api/bookings/{id}     # Annuler
```

### Favoris

```
GET    /api/favorites                 # Mes favoris
POST   /api/favorites/{package_id}    # Ajouter
DELETE /api/favorites/{package_id}    # Supprimer
GET    /api/favorites/check/{id}      # Verifier si favori
```

### TripAdvisor

```
GET /api/tripadvisor/locations        # Hotels
GET /api/tripadvisor/locations/{id}   # Details hotel
GET /api/tripadvisor/photos/{id}      # Photos
GET /api/tripadvisor/reviews/{id}     # Avis
```

### Chat IA

```
POST /api/conversations/new              # Nouvelle conversation
GET  /api/conversations/{id}             # Recuperer
POST /api/conversations/{id}/message     # Envoyer message
DELETE /api/conversations/{id}           # Supprimer
```

### Health

```
GET /api/health    # Status de l'API
GET /api/ready     # Readiness (verifie la connexion Oracle)
```

---

## Frontend

### Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Accueil avec packages populaires |
| `/search` | Search | Recherche avec filtres |
| `/packages/:id` | PackageDetail | Details d'un package + formulaire reservation |
| `/hotels` | Hotels | Hotels TripAdvisor |
| `/hotels/:locationId` | HotelDetail | Details d'un hotel + photos + avis |
| `/favorites` | Favorites | Mes favoris |
| `/bookings` | Bookings | Mes reservations |
| `/profile` | Profile | Profil utilisateur + avatar |
| `/login` | Login | Connexion |
| `/signup` | SignUp | Inscription |

### Composants principaux

- **Layout** : Structure commune (Header + contenu + Footer)
- **ChatWidget** : Widget de chat flottant (assistant IA)
- **PackageCard** : Carte d'affichage d'un package

---

## Import TripAdvisor

Le script `scripts/seed_oracle.py` fetche automatiquement les donnees TripAdvisor (hotels, photos, avis) pour 15 pays et seed les destinations + packages.

```bash
# Variable d'env optionnelle (cle par defaut incluse)
export TRIPADVISOR_API_KEY=votre_cle

python scripts/seed_oracle.py
```

---

## PageContext (Contexte de page pour l'agent IA)

L'agent IA connait la page que l'utilisateur consulte et les donnees affichees. Cela permet des interactions comme "reserve celui-ci" ou "montre-moi le premier" sans ambiguite.

### Fonctionnement

1. **`PageContext`** (React Context) stocke les infos de la page courante (page, route, donnees)
2. Chaque page met a jour ce contexte via `useSetPageContext()` dans un `useEffect`
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

### Exemples d'utilisation

- Sur PackageDetail: "reserve celui-ci pour 2 personnes le 15 juin" -> l'agent connait le package
- Sur Search: "montre-moi plus de details sur le premier" -> l'agent connait les resultats
- Sur Bookings: "annule ma derniere reservation" -> l'agent voit la liste des bookings

### Navigation automatique apres action de l'agent

| Action agent | Navigation automatique |
|-------------|----------------------|
| Reservation confirmee (`booking_confirmed`) | `/bookings` |
| Ajout aux favoris (`add_favorite`) | `/favorites` |

---

## Logging

Le backend dispose d'un systeme de logging centralise qui ecrit dans `backend/log_apps/`.

### Fichiers de logs

| Fichier | Contenu | Niveau |
|---------|---------|--------|
| `app.log` | Logs generaux de l'application | INFO+ |
| `agents.log` | Activite des agents IA (orchestrateur, UI, database) | DEBUG+ |
| `sql.log` | Toutes les requetes SQL (SELECT, INSERT, UPDATE, DELETE) | DEBUG+ |
| `errors.log` | Erreurs de tous les loggers | ERROR+ |

### Configuration

- **Fichier** : `backend/logging_config.py`
- **Rotation** : 5 MB max par fichier, 3 backups
- **Volume K8s** : hostPath monte depuis le pod vers `backend/log_apps/` local
- Les logs sont disponibles en temps reel dans le repo local

### Consultation

```bash
# Logs generaux
cat backend/log_apps/app.log

# Requetes SQL
cat backend/log_apps/sql.log

# Activite des agents IA
cat backend/log_apps/agents.log

# Erreurs uniquement
cat backend/log_apps/errors.log
```

---

## Protocole A2A

Le backend utilise le protocole Agent-to-Agent (A2A) de Google pour la coordination des agents IA.

### Agents

| Agent | Description |
|-------|-------------|
| **Orchestrator** | Coordonne les autres agents (LangGraph) |
| **Database** | Requetes Oracle (LangChain tools) |
| **UI** | Actions interface utilisateur |

### Endpoints A2A

```
GET  /.well-known/agent.json    # Agent Card (metadonnees)
POST /a2a/tasks                  # Creer une tache
GET  /a2a/tasks/{id}            # Status d'une tache
POST /a2a/tasks/{id}/messages   # Envoyer un message
POST /a2a/tasks/{id}/cancel     # Annuler une tache
```

---

## Developpement

### Sans Docker/K8s (dev local)

#### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Oracle doit tourner sur localhost:1521
uvicorn api.main:app --reload --port 8000
```

#### Frontend

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
# Supprimer K8s
kubectl delete -f k8s/

# Supprimer Oracle
docker compose down

# Recreer
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
