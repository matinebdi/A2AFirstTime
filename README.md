# VacanceAI - Plateforme de Réservation de Vacances

Application complète de réservation de vacances avec assistant IA, intégration TripAdvisor et architecture microservices.

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
- Une recherche sémantique via RAG (pgvector)
- Une architecture Agent-to-Agent (A2A) pour l'orchestration IA

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
- Architecture microservices
- Protocole A2A pour communication inter-agents
- Base de données PostgreSQL avec Row Level Security
- Recherche vectorielle (embeddings)

---

## Stack Technique

| Couche | Technologies |
|--------|--------------|
| **Frontend** | React 18, TypeScript, Vite, Tailwind CSS |
| **Backend** | Python 3.12, FastAPI, Uvicorn |
| **Base de données** | Supabase (PostgreSQL 15), pgvector |
| **IA** | Google Gemini, LangChain, LangGraph |
| **Auth** | Supabase Auth (JWT) |
| **Storage** | Supabase Storage (S3-compatible) |
| **Conteneurisation** | Docker, Docker Compose |

---

## Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         FRONTEND                                 │
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
└─────────────────────────┬───────────────────────────────────────┘
                          │ PostgreSQL
┌─────────────────────────▼───────────────────────────────────────┐
│                        SUPABASE                                  │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │  PostgreSQL  │  │    Auth      │  │   Storage    │          │
│  │  + pgvector  │  │    JWT       │  │   (Images)   │          │
│  └──────────────┘  └──────────────┘  └──────────────┘          │
│                    localhost:54321                               │
└─────────────────────────────────────────────────────────────────┘
```

### Structure des dossiers

```
ui-automation-a2a/
├── backend/
│   ├── api/
│   │   ├── main.py                 # Point d'entrée FastAPI
│   │   └── routes/
│   │       ├── auth.py             # Authentification
│   │       ├── packages.py         # Packages vacances
│   │       ├── bookings.py         # Réservations
│   │       ├── favorites.py        # Favoris
│   │       ├── reviews.py          # Avis
│   │       ├── destinations.py     # Destinations
│   │       ├── conversations.py    # Chat IA
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
│   │   └── middleware.py           # Middleware JWT
│   ├── database/
│   │   └── supabase_client.py      # Client Supabase
│   ├── config.py                   # Configuration
│   ├── requirements.txt            # Dépendances Python
│   └── Dockerfile
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── common/
│   │   │   │   ├── Header.tsx      # Navigation
│   │   │   │   └── Footer.tsx      # Pied de page
│   │   │   ├── chat/
│   │   │   │   └── ChatWidget.tsx  # Widget chatbot
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
│   │   │   ├── supabase.ts         # Client Supabase
│   │   │   └── tripadvisor.ts      # Service TripAdvisor
│   │   ├── contexts/
│   │   │   └── AuthContext.tsx     # Context auth
│   │   ├── hooks/
│   │   │   └── useChat.ts          # Hook chat
│   │   ├── types/
│   │   │   └── index.ts            # Types TypeScript
│   │   ├── App.tsx                 # Routes
│   │   ├── main.tsx                # Entry point
│   │   └── index.css               # Styles Tailwind
│   ├── package.json
│   ├── vite.config.ts
│   ├── tailwind.config.js
│   ├── tsconfig.json
│   └── Dockerfile
│
├── supabase/
│   ├── config.toml                 # Config Supabase
│   └── migrations/
│       ├── 20260115000000_initial_schema.sql
│       └── 20260116000000_tripadvisor_import.sql
│
├── scripts/
│   └── tripadvise.ipynb            # Script import TripAdvisor
│
├── .env                            # Variables d'environnement
├── .gitignore
├── compose.yaml                    # Docker Compose
├── CLAUDE.md                       # Instructions Claude Code
└── README.md                       # Ce fichier
```

---

## Installation

### Prérequis

- **Docker Desktop** (v24+)
- **Node.js** (v20+)
- **Git**

### Étape 1 : Cloner le repository

```bash
git clone <repository-url>
cd ui-automation-a2a
```

### Étape 2 : Installer Supabase CLI

```bash
npm install -g supabase
```

### Étape 3 : Démarrer Supabase local

```bash
npx supabase start
```

Attendre que tous les services démarrent (~2 minutes la première fois).

### Étape 4 : Récupérer les clés

```bash
npx supabase status
```

Copier les valeurs `anon key` et `service_role key`.

---

## Configuration

Créer un fichier `.env` à la racine du projet :

```env
# =============================================
# VacanceAI - Environment Variables
# =============================================

# Supabase Local (from: npx supabase status)
SUPABASE_URL=http://127.0.0.1:54321

# Authentication Keys
ANON_KEY=<votre_anon_key>
SERVICE_ROLE_KEY=<votre_service_role_key>

# Database
DATABASE_URL=postgresql://postgres:postgres@127.0.0.1:54322/postgres

# Google AI (Gemini)
GOOGLE_API_KEY=<votre_gemini_api_key>
```

---

## Lancement

### Avec Docker (recommandé)

```bash
# Appliquer les migrations
npx supabase db reset

# Construire et lancer
docker compose up --build

# Ou en arrière-plan
docker compose up -d --build
```

### URLs disponibles

| Service | URL | Description |
|---------|-----|-------------|
| Frontend | http://localhost:5173 | Application React |
| Backend API | http://localhost:8080 | API FastAPI |
| Supabase Studio | http://localhost:54323 | Admin DB |
| Supabase API | http://localhost:54321 | API Supabase |

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

### Schéma principal

#### `destinations`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| name | TEXT | Nom de la destination |
| country | TEXT | Pays |
| city | TEXT | Ville |
| description | TEXT | Description |
| image_url | TEXT | Image principale |
| tags | TEXT[] | Tags (plage, montagne...) |
| average_rating | DECIMAL | Note moyenne |

#### `packages`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| destination_id | UUID | FK destination |
| name | TEXT | Nom du package |
| description | TEXT | Description |
| duration_days | INT | Durée en jours |
| price_per_person | DECIMAL | Prix par personne |
| max_persons | INT | Nombre max de personnes |
| includes | JSONB | Ce qui est inclus |
| available_from | DATE | Disponible à partir de |
| available_to | DATE | Disponible jusqu'à |
| is_active | BOOLEAN | Actif ou non |
| images | TEXT[] | URLs des images |

#### `bookings`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| user_id | UUID | FK utilisateur |
| package_id | UUID | FK package |
| status | TEXT | pending/confirmed/cancelled/completed |
| start_date | DATE | Date de début |
| end_date | DATE | Date de fin |
| num_persons | INT | Nombre de personnes |
| total_price | DECIMAL | Prix total |
| payment_status | TEXT | unpaid/paid/refunded |

### Tables TripAdvisor

#### `tripadvisor_locations`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| location_id | TEXT | ID TripAdvisor |
| name | TEXT | Nom de l'hotel |
| address_obj | JSONB | Adresse complète |
| search_country | TEXT | Pays de recherche |
| category | TEXT | hotels/restaurants/attractions |

#### `tripadvisor_photos`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| location_id | TEXT | FK location |
| photo_id | TEXT | ID photo TripAdvisor |
| url_original | TEXT | URL originale |
| url_large | TEXT | URL grande taille |
| url_medium | TEXT | URL moyenne taille |
| url_small | TEXT | URL petite taille |
| caption | TEXT | Légende |
| storage_path | TEXT | Chemin Supabase Storage |

#### `tripadvisor_reviews`
| Colonne | Type | Description |
|---------|------|-------------|
| id | UUID | Identifiant unique |
| location_id | TEXT | FK location |
| review_id | TEXT | ID review TripAdvisor |
| rating | INT | Note (1-5) |
| title | TEXT | Titre |
| text | TEXT | Contenu |
| published_date | TEXT | Date de publication |
| user_name | TEXT | Nom de l'auteur |

### Row Level Security (RLS)

- **Destinations & Packages** : Lecture publique
- **Bookings & Favorites** : L'utilisateur accède uniquement à ses données
- **Reviews** : Lecture publique, création authentifiée
- **Conversations** : L'utilisateur accède uniquement à ses conversations
- **TripAdvisor** : Lecture publique

---

## API Backend

### Authentification

```
POST /api/auth/signup
POST /api/auth/login
POST /api/auth/logout
GET  /api/auth/me
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
- **supabase.ts** : Client Supabase direct
- **tripadvisor.ts** : Service données TripAdvisor

---

## Import TripAdvisor

### Prérequis

- Clé API TripAdvisor Content API
- Jupyter ou VS Code avec extension Jupyter

### Exécution

1. Ouvrir `scripts/tripadvise.ipynb`

2. **Cellule 1** : Importer les hotels
   - Configure la liste des pays
   - Fetch les hotels via l'API
   - Résultat : DataFrame `df`

3. **Cellule 2** : Importer les photos
   - Boucle sur les `location_id`
   - Résultat : DataFrame `df_photos`

4. **Cellule 3** : Importer les reviews
   - Boucle sur les `location_id`
   - Résultat : DataFrame `df_reviews`

5. **Cellule 4** : Connexion Supabase
   - Initialise le client

6. **Cellule 5-7** : Insert dans Supabase
   - Insert locations, photos, reviews

7. **Cellule 8** (optionnel) : Upload images
   - Télécharge et stocke dans Supabase Storage

### Headers requis

L'API TripAdvisor nécessite ces headers :

```python
headers = {
    "accept": "application/json",
    "Referer": "https://tripadvisor-content-api.readme.io/",
    "Origin": "https://tripadvisor-content-api.readme.io"
}
```

---

## Protocole A2A

Le backend utilise le protocole Agent-to-Agent (A2A) de Google pour la coordination des agents IA.

### Agents disponibles

| Agent | Description |
|-------|-------------|
| **Orchestrator** | Coordonne les autres agents |
| **Database** | Requêtes Supabase |
| **UI** | Actions interface utilisateur |

### Endpoints A2A

```
GET  /.well-known/agent.json    # Agent Card (métadonnées)
POST /a2a/tasks                  # Créer une tâche
GET  /a2a/tasks/{id}            # Status d'une tâche
POST /a2a/tasks/{id}/messages   # Envoyer un message
POST /a2a/tasks/{id}/cancel     # Annuler une tâche
```

### Agent Card

```json
{
  "name": "vacanceai-orchestrator",
  "description": "VacanceAI main orchestrator agent",
  "url": "http://localhost:8080",
  "version": "1.0.0",
  "capabilities": {
    "streaming": true,
    "push_notifications": false
  },
  "skills": [
    {
      "id": "search_packages",
      "name": "Search Packages",
      "description": "Search vacation packages"
    }
  ]
}
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

# Lancer
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

### Tests

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm run test
```

### Linting

```bash
# Frontend
cd frontend
npm run lint
```

---

## Troubleshooting

### Erreur "Module not found"

```bash
docker compose down
docker compose up --build
```

### Erreur Supabase 502

```bash
npx supabase stop
npx supabase start
```

### Erreur CORS

Vérifier que `FRONTEND_URL` dans compose.yaml correspond à l'URL du frontend.

### Reset complet

```bash
docker compose down -v
npx supabase stop
npx supabase start
npx supabase db reset
docker compose up --build
```

---

## Licence

MIT

---

## Auteurs

VacanceAI Team
