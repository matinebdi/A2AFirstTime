# VacanceAI - Plateforme de Réservation de Vacances

Application complète de réservation de vacances avec assistant IA, intégration TripAdvisor et protocole Agent-to-Agent (A2A).

---

## Table des matières

1. [Présentation](#présentation)
2. [Fonctionnalités](#fonctionnalités)
3. [Stack Technique](#stack-technique)
4. [Architecture](#architecture)
5. [Installation](#installation)
6. [Configuration](#configuration)
7. [Lancement](#lancement)
8. [Base de données](#base-de-données)
9. [API Backend](#api-backend)
10. [Frontend](#frontend)
11. [Import TripAdvisor](#import-tripadvisor)
12. [Protocole A2A](#protocole-a2a)
13. [Développement](#développement)

---

## Présentation

**VacanceAI** est une plateforme moderne de réservation de vacances qui combine :

- Un catalogue de packages vacances tout compris
- Des données hotels en temps réel via TripAdvisor
- Un assistant IA intelligent (Google Gemini)
- Une architecture Agent-to-Agent (A2A) pour l'orchestration IA
- Authentification JWT custom avec refresh tokens

---

## Fonctionnalités

### Pour les utilisateurs
- Recherche de packages vacances avec filtres (prix, durée, destination)
- Consultation des hotels TripAdvisor avec photos et avis
- Réservation en ligne
- Gestion des favoris
- Historique des réservations
- Chat avec assistant IA

### Pour les développeurs
- API REST complète
- Protocole A2A pour communication inter-agents
- Base de données Oracle 21c XE
- Observabilité avec OpenTelemetry + Jaeger

---

## Stack Technique

| Couche | Technologies |
|--------|--------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Base de données** | Oracle 21c XE |
| **IA** | Google Gemini |
| **Auth** | JWT custom (PyJWT + passlib bcrypt) |
| **Observabilité** | OpenTelemetry, Jaeger |
| **Conteneurisation** | Docker, Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                │
│                    React + TypeScript                            │
│                    localhost:5173                                │
└─────────────────────────┬───────────────────────────────────────┘
                          │ HTTP/REST
┌─────────────────────────▼───────────────────────────────────────┐
│                         BACKEND                                  │
│                    FastAPI + Python                              │
│                    localhost:8080                                │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   API REST   │  │  A2A Server  │  │   Agents     │          │
│  │   /api/*     │  │  /a2a/*      │  │ Orchestrator │          │
│  └──────────────┘  └──────────────┘  │  Database    │          │
│                                       │  UI          │          │
│                                       └──────────────┘          │
└───────────┬───────────────────────────────────┬─────────────────┘
            │ oracledb (thin mode)              │ OTLP
┌───────────▼───────────────┐    ┌──────────────▼─────────────────┐
│       ORACLE 21c XE       │    │           JAEGER               │
│  ┌──────────────────────┐ │    │    Traces OpenTelemetry        │
│  │  Schema VACANCEAI    │ │    │    localhost:16686              │
│  │  11 tables + triggers│ │    └────────────────────────────────┘
│  └──────────────────────┘ │
│       localhost:1521      │
└───────────────────────────┘
```

### Structure des dossiers

```
ui-automation-a2a/
├── backend/
│   ├── api/
│   │   ├── main.py                 # Point d'entrée FastAPI
│   │   └── routes/
│   │       ├── auth.py             # Authentification (JWT)
│   │       ├── packages.py         # Packages vacances
│   │       ├── bookings.py         # Réservations
│   │       ├── favorites.py        # Favoris
│   │       ├── reviews.py          # Avis
│   │       ├── destinations.py     # Destinations
│   │       ├── conversations.py    # Chat IA
│   │       ├── tripadvisor.py      # Données TripAdvisor
│   │       └── health.py           # Health check
│   ├── agents/
│   │   ├── base.py                 # Classe agent de base
│   │   ├── orchestrator/           # Agent coordinateur
│   │   ├── database/               # Agent requêtes DB
│   │   └── ui/                     # Agent UI
│   ├── a2a/
│   │   ├── protocol.py             # Schémas A2A
│   │   ├── client.py               # Client A2A
│   │   └── server.py               # Serveur A2A
│   ├── auth/
│   │   ├── jwt_service.py          # Service JWT (PyJWT + bcrypt)
│   │   └── middleware.py           # Middleware auth
│   ├── database/
│   │   ├── oracle_client.py        # Client Oracle (oracledb thin)
│   │   ├── oracle_schema.sql       # Schéma complet (11 tables)
│   │   └── queries.py              # Requêtes SQL centralisées
│   ├── config.py                   # Configuration (pydantic-settings)
│   ├── telemetry.py                # OpenTelemetry setup
│   ├── requirements.txt
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx      # Navigation
│   │   │   │   └── Footer.tsx      # Pied de page
│   │   │   ├── chat/
│   │   │   │   ├── ChatWidget.tsx  # Widget chatbot
│   │   │   │   └── ChatErrorBoundary.tsx
│   │   │   ├── packages/
│   │   │   │   └── PackageCard.tsx # Carte package
│   │   │   └── Layout.tsx          # Layout principal
│   │   ├── pages/
│   │   │   ├── Home.tsx            # Accueil
│   │   │   ├── Search.tsx          # Recherche
│   │   │   ├── Hotels.tsx          # Hotels TripAdvisor
│   │   │   ├── Bookings.tsx        # Réservations
│   │   │   ├── Login.tsx           # Connexion
│   │   │   └── SignUp.tsx          # Inscription
│   │   ├── services/
│   │   │   ├── api.ts              # Client API backend
│   │   │   └── tripadvisor.ts      # Service TripAdvisor
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx     # Context auth (localStorage)
│   │   ├── hooks/
│   │   │   └── useChat.ts          # Hook chat
│   │   ├── types/
│   │   │   └── index.ts            # Types TypeScript
│   │   ├── utils/
│   │   │   ├── telemetry.ts        # OpenTelemetry frontend
│   │   │   └── uuid.ts             # UUID helpers
│   │   ├── App.tsx                 # Routes
│   │   ├── main.tsx                # Entry point
│   │   └── index.css               # Styles Tailwind
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── scripts/
│   ├── tripadvise.ipynb            # Script import TripAdvisor
│   ├── seed_oracle.py              # Seed données Oracle
│   └── scraper/data/seed_data.sql  # Données de seed SQL
│
├── .env                            # Variables d'environnement
├── .gitignore
├── compose.yaml                    # Docker Compose
├── CLAUDE.md                       # Instructions Claude Code
└── README.md
```

---

## Installation

### Prérequis

- **Docker Desktop** (v24+)
- **Git**

### Étape 1 : Cloner le repository

```bash
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
```

### Étape 2 : Créer le volume Oracle

```bash
docker volume create oracle-xe-data
```

---

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
# =============================================
# VacanceAI - Environment Variables
# =============================================

# Oracle Database
ORACLE_USER=VACANCEAI
ORACLE_PASSWORD=vacanceai

# JWT Auth
JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

# Google AI (Gemini)
GOOGLE_API_KEY=<votre_gemini_api_key>
```

---

## Lancement

### Avec Docker (recommandé)

```bash
# Construire et lancer (Oracle + Jaeger + Backend + Frontend)
docker compose up --build

# Ou en arrière-plan
docker compose up -d --build
```

> **Note** : Le premier lancement d'Oracle peut prendre ~2 minutes. Le backend attend que Oracle soit healthy avant de démarrer.

### Initialiser la base de données

Exécuter le schéma SQL dans Oracle :

```bash
# Se connecter à Oracle et exécuter le schéma
docker exec -i oracle-xe sqlplus SYS/admin@//localhost:1521/XE as SYSDBA < backend/database/oracle_schema.sql

# Puis seed les données
python scripts/seed_oracle.py
```

### URLs disponibles

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Application React |
| Backend API | http://localhost:8080 | API FastAPI |
| Swagger UI | http://localhost:8080/swagger | Documentation API interactive |
| ReDoc | http://localhost:8080/redoc | Documentation API (alternative) |
| Jaeger UI | http://localhost:16686 | Traces OpenTelemetry |
| Oracle | localhost:1521/XE | Base de données |

### Commandes Docker

```bash
# Voir les logs
docker compose logs -f

# Logs d'un service spécifique
docker compose logs -f backend
docker compose logs -f frontend

# Arrêter
docker compose down

# Reconstruire un service
docker compose up --build backend

# Redémarrer
docker compose restart
```

---

## Base de données

### Oracle 21c XE

- **User** : `VACANCEAI` / `vacanceai`
- **Schema** : `backend/database/oracle_schema.sql` (11 tables + triggers)
- **Client** : `oracledb` en mode thin (pas d'Oracle Instant Client requis)
- **Connection pool** : géré via `backend/database/oracle_client.py`

### Conventions Oracle

| PostgreSQL (ancien) | Oracle (actuel) |
|---------------------|-----------------|
| `BOOLEAN` | `NUMBER(1)` |
| `UUID` | `VARCHAR2(36)` + `SYS_GUID()` |
| `JSONB` | `CLOB` avec contrainte `IS JSON` |
| `TEXT[]` | `CLOB` (JSON array) |
| `SERIAL` | Triggers + sequences |
| `LIMIT/OFFSET` | `OFFSET :n ROWS FETCH NEXT :m ROWS ONLY` |

### Tables principales

#### `destinations`
| Colonne | Type | Description |
|---------|------|-------------|
| id | VARCHAR2(36) | UUID (SYS_GUID) |
| name | VARCHAR2(255) | Nom de la destination |
| country | VARCHAR2(100) | Pays |
| city | VARCHAR2(100) | Ville |
| description | CLOB | Description |
| image_url | VARCHAR2(500) | Image principale |
| tags | CLOB (JSON) | Tags (plage, montagne...) |
| average_rating | NUMBER(3,2) | Note moyenne |

#### `packages`
| Colonne | Type | Description |
|---------|------|-------------|
| id | VARCHAR2(36) | UUID |
| destination_id | VARCHAR2(36) | FK destination |
| name | VARCHAR2(255) | Nom du package |
| description | CLOB | Description |
| duration_days | NUMBER | Durée en jours |
| price_per_person | NUMBER(10,2) | Prix par personne |
| max_persons | NUMBER | Nombre max de personnes |
| includes | CLOB (JSON) | Ce qui est inclus |
| is_active | NUMBER(1) | Actif ou non |
| images | CLOB (JSON) | URLs des images |

#### `bookings`
| Colonne | Type | Description |
|---------|------|-------------|
| id | VARCHAR2(36) | UUID |
| user_id | VARCHAR2(36) | FK utilisateur |
| package_id | VARCHAR2(36) | FK package |
| status | VARCHAR2(20) | pending/confirmed/cancelled/completed |
| start_date | DATE | Date de début |
| end_date | DATE | Date de fin |
| num_persons | NUMBER | Nombre de personnes |
| total_price | NUMBER(10,2) | Prix total |
| payment_status | VARCHAR2(20) | unpaid/paid/refunded |

### Tables TripAdvisor

#### `tripadvisor_locations`
| Colonne | Type | Description |
|---------|------|-------------|
| id | VARCHAR2(36) | UUID |
| location_id | VARCHAR2(50) | ID TripAdvisor |
| name | VARCHAR2(255) | Nom de l'hotel |
| address_obj | CLOB (JSON) | Adresse complète |
| search_country | VARCHAR2(100) | Pays de recherche |
| category | VARCHAR2(50) | hotels/restaurants/attractions |

#### `tripadvisor_photos` / `tripadvisor_reviews`
Mêmes structures avec URLs des images et données d'avis.

---

## API Backend

### Authentification (JWT custom)

```
POST /api/auth/signup          # Inscription
POST /api/auth/login           # Connexion → access_token + refresh_token
POST /api/auth/refresh         # Renouveler le token
POST /api/auth/logout          # Déconnexion
GET  /api/auth/me              # Profil utilisateur
```

Les tokens sont stockés dans `localStorage` côté frontend. Les refresh tokens sont stockés en base dans la table `refresh_tokens` et rotés à chaque refresh.

### Destinations

```
GET /api/destinations
GET /api/destinations/{id}
```

### Packages

```
GET  /api/packages                    # Liste avec filtres
GET  /api/packages/featured           # Packages populaires
GET  /api/packages/{id}               # Détails
GET  /api/packages/{id}/availability  # Vérifier disponibilité
```

**Paramètres de recherche :**
- `destination` : ID destination
- `min_price`, `max_price` : Fourchette de prix
- `min_duration`, `max_duration` : Durée
- `start_date` : Date de départ
- `limit`, `offset` : Pagination

### Réservations

```
GET   /api/bookings           # Mes réservations
GET   /api/bookings/{id}      # Détails
POST  /api/bookings           # Créer
PATCH /api/bookings/{id}      # Modifier
DELETE /api/bookings/{id}     # Annuler
```

### Favoris

```
GET    /api/favorites                 # Mes favoris
POST   /api/favorites/{package_id}    # Ajouter
DELETE /api/favorites/{package_id}    # Supprimer
GET    /api/favorites/check/{id}      # Vérifier si favori
```

### TripAdvisor

```
GET /api/tripadvisor/locations        # Hotels
GET /api/tripadvisor/locations/{id}   # Détails hotel
GET /api/tripadvisor/photos/{id}      # Photos
GET /api/tripadvisor/reviews/{id}     # Avis
```

### Conversations (Chat IA)

```
POST /api/conversations/new              # Nouvelle conversation
GET  /api/conversations/{id}             # Récupérer
POST /api/conversations/{id}/message     # Envoyer message
DELETE /api/conversations/{id}           # Supprimer
```

### Health

```
GET /api/health    # Status de l'API
```

---

## Frontend

### Pages

| Route | Page | Description |
|-------|------|-------------|
| `/` | Home | Accueil avec packages populaires |
| `/search` | Search | Recherche avec filtres |
| `/hotels` | Hotels | Hotels TripAdvisor |
| `/bookings` | Bookings | Mes réservations |
| `/login` | Login | Connexion |
| `/signup` | SignUp | Inscription |

### Composants principaux

- **Layout** : Structure commune (Header + contenu + Footer)
- **Header** : Navigation avec menu responsive
- **ChatWidget** : Widget de chat flottant (IA)
- **PackageCard** : Carte d'affichage d'un package

### Services

- **api.ts** : Client Axios pour le backend
- **tripadvisor.ts** : Service données TripAdvisor

---

## Import TripAdvisor

### Prérequis

- Clé API TripAdvisor Content API (variable d'env `TRIPADVISOR_API_KEY`)
- Jupyter ou VS Code avec extension Jupyter

### Exécution

1. Ouvrir `scripts/tripadvise.ipynb`
2. Définir les variables d'environnement (`TRIPADVISOR_API_KEY`, `SUPABASE_SERVICE_KEY`)
3. Exécuter les cellules dans l'ordre : fetch hotels → photos → reviews → insert en base

---

## Protocole A2A

Le backend utilise le protocole Agent-to-Agent (A2A) de Google pour la coordination des agents IA.

### Agents disponibles

| Agent | Description |
|-------|-------------|
| **Orchestrator** | Coordonne les autres agents |
| **Database** | Requêtes Oracle |
| **UI** | Actions interface utilisateur |

### Endpoints A2A

```
GET  /.well-known/agent.json    # Agent Card (métadonnées)
POST /a2a/tasks                  # Créer une tâche
GET  /a2a/tasks/{id}            # Status d'une tâche
POST /a2a/tasks/{id}/messages   # Envoyer un message
POST /a2a/tasks/{id}/cancel     # Annuler une tâche
```

---

## Développement

### Sans Docker

#### Backend

```bash
cd backend

# Créer environnement virtuel
python -m venv venv
source venv/bin/activate  # Linux/Mac
.\venv\Scripts\activate   # Windows

# Installer dépendances
pip install -r requirements.txt

# Lancer (Oracle doit tourner sur localhost:1521)
uvicorn api.main:app --reload --port 8000
```

#### Frontend

```bash
cd frontend

# Installer dépendances
npm install

# Lancer
npm run dev
```

---

## Troubleshooting

### Erreur "Module not found"

```bash
docker compose down
docker compose up --build
```

### Oracle ne démarre pas

```bash
# Vérifier que le volume existe
docker volume ls | grep oracle-xe-data

# Créer si manquant
docker volume create oracle-xe-data

# Vérifier les logs
docker compose logs oracle
```

### Erreur CORS

Vérifier que `FRONTEND_URL` dans compose.yaml correspond à l'URL du frontend.

### Reset complet

```bash
docker compose down -v
docker volume create oracle-xe-data
docker compose up --build
```

---

## Licence

MIT

---

## Auteurs

VacanceAI Team
