# Diagramme des API Endpoints - Backend VacanceAI

![Diagramme API Endpoints](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-074628.png)

## Description

Ce diagramme represente les 40 endpoints exposes par le backend FastAPI de VacanceAI, organises en 9 routers. Chaque router correspond a un fichier dans `backend/api/routes/`.

---

## Vue d'ensemble

| Router | Prefixe | Endpoints | Auth requise |
|--------|---------|-----------|--------------|
| Auth | `/api/auth` | 8 | Partielle |
| Packages | `/api/packages` | 4 | Non |
| Bookings | `/api/bookings` | 5 | Oui |
| Favorites | `/api/favorites` | 4 | Oui |
| Reviews | `/api/reviews` | 2 | Partielle |
| Destinations | `/api/destinations` | 3 | Non |
| Conversations | `/api/conversations` | 5 | Optionnelle |
| TripAdvisor | `/api/tripadvisor` | 6 | Non |
| Health | `/api` | 2 | Non |
| **Total** | | **39 REST + 1 WebSocket** | |

---

## Auth (`backend/api/routes/auth.py`)

Gestion de l'authentification JWT avec refresh tokens.

| Methode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| POST | `/api/auth/signup` | Inscription (email, password, first_name, last_name) | Non |
| POST | `/api/auth/login` | Connexion -> access_token + refresh_token | Non |
| POST | `/api/auth/logout` | Deconnexion (revoque le refresh token) | Oui |
| POST | `/api/auth/refresh` | Renouvellement du token (rotation du refresh) | Non |
| GET | `/api/auth/me` | Profil utilisateur courant | Oui |
| PATCH | `/api/auth/me` | Modifier le profil (first_name, last_name, phone, avatar_url) | Oui |
| POST | `/api/auth/avatar` | Upload d'avatar (jpg/png/webp, max 2 MB) | Oui |
| GET | `/api/auth/avatar/{filename}` | Telecharger un avatar | Non |

---

## Packages (`backend/api/routes/packages.py`)

Consultation du catalogue de packages vacances.

| Methode | Endpoint | Description | Parametres |
|---------|----------|-------------|------------|
| GET | `/api/packages` | Liste avec filtres | `destination`, `destination_id`, `min_price`, `max_price`, `min_duration`, `max_duration`, `tags`, `start_date`, `sort_by`, `limit`, `offset` |
| GET | `/api/packages/featured` | Packages populaires | `limit` (1-20, defaut 6) |
| GET | `/api/packages/{id}` | Details d'un package + destination + avis | - |
| GET | `/api/packages/{id}/availability` | Verification de disponibilite | `start_date` (requis), `num_persons` (1-10) |

**Tri disponible** (`sort_by`) : `price_asc`, `price_desc`, `duration_asc`, `duration_desc`, `name_asc`

---

## Bookings (`backend/api/routes/bookings.py`)

Gestion des reservations. Tous les endpoints necessitent une authentification.

| Methode | Endpoint | Description | Body |
|---------|----------|-------------|------|
| GET | `/api/bookings` | Mes reservations (avec package + destination) | `status` (filtre optionnel) |
| POST | `/api/bookings` | Creer une reservation | `package_id`, `start_date`, `num_persons`, `special_requests?` |
| GET | `/api/bookings/{id}` | Details d'une reservation | - |
| PATCH | `/api/bookings/{id}` | Modifier (statut, demandes speciales) | `status?`, `special_requests?` |
| DELETE | `/api/bookings/{id}` | Supprimer une reservation | - |

---

## Favorites (`backend/api/routes/favorites.py`)

Gestion des favoris. Tous les endpoints necessitent une authentification.

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/api/favorites` | Mes favoris (avec package + destination) |
| POST | `/api/favorites/{package_id}` | Ajouter un package aux favoris |
| DELETE | `/api/favorites/{package_id}` | Retirer un package des favoris |
| GET | `/api/favorites/check/{package_id}` | Verifier si un package est en favori |

---

## Reviews (`backend/api/routes/reviews.py`)

Avis sur les packages.

| Methode | Endpoint | Description | Auth |
|---------|----------|-------------|------|
| GET | `/api/reviews/package/{package_id}` | Avis d'un package (avec infos auteur) | Non |
| POST | `/api/reviews` | Publier un avis (rating 1-5, commentaire) | Oui |

**Parametres GET** : `limit` (1-50, defaut 10), `offset` (defaut 0)

---

## Destinations (`backend/api/routes/destinations.py`)

Consultation des destinations.

| Methode | Endpoint | Description | Parametres |
|---------|----------|-------------|------------|
| GET | `/api/destinations` | Liste des destinations | `country`, `tags` (comma-separated), `limit` (1-100, defaut 20) |
| GET | `/api/destinations/{id}` | Details + packages associes | - |
| GET | `/api/destinations/{id}/packages` | Packages d'une destination | `min_price`, `max_price` |

---

## Conversations (`backend/api/routes/conversations.py`)

Chat avec l'assistant IA. Authentification optionnelle (lie la conversation a l'utilisateur si connecte).

| Methode | Endpoint | Description |
|---------|----------|-------------|
| **WS** | `/api/conversations/ws/{id}` | **WebSocket** temps reel (message + contexte page) |
| POST | `/api/conversations/{id}/message` | Envoyer un message (fallback REST) |
| GET | `/api/conversations/{id}` | Historique de la conversation |
| DELETE | `/api/conversations/{id}` | Supprimer une conversation |
| POST | `/api/conversations/new` | Creer une nouvelle conversation |

### Format WebSocket

**Envoi** :
```json
{
  "message": "Reserve celui-ci pour 2 personnes",
  "context": {
    "user": {"id": "...", "email": "..."},
    "page": {"page": "package_detail", "data": {"package_id": "..."}}
  }
}
```

**Reception** :
```json
{
  "response": "Reservation confirmee !",
  "ui_actions": [{"action": "booking_confirmed", "data": {...}}],
  "agent_type": "ui",
  "timestamp": "2026-02-13T..."
}
```

---

## TripAdvisor (`backend/api/routes/tripadvisor.py`)

Donnees hotels importees depuis TripAdvisor.

| Methode | Endpoint | Description | Parametres |
|---------|----------|-------------|------------|
| GET | `/api/tripadvisor/locations` | Liste des hotels | `country` |
| GET | `/api/tripadvisor/locations-with-details` | Hotels + photos + avis + rating moyen (optimise, une seule requete) | `country` |
| GET | `/api/tripadvisor/countries` | Liste des pays disponibles | - |
| GET | `/api/tripadvisor/locations/{id}` | Details d'un hotel | - |
| GET | `/api/tripadvisor/locations/{id}/photos` | Photos d'un hotel | - |
| GET | `/api/tripadvisor/locations/{id}/reviews` | Avis d'un hotel | - |

**Note** : L'endpoint `/locations-with-details` utilise `joinedload()` pour charger photos et avis en une seule requete SQL, evitant les N+1 queries.

---

## Health (`backend/api/routes/health.py`)

Probes Kubernetes pour le monitoring.

| Methode | Endpoint | Description | Code si erreur |
|---------|----------|-------------|----------------|
| GET | `/api/health` | Liveness probe (toujours 200) | - |
| GET | `/api/ready` | Readiness probe (verifie la connexion Oracle) | 503 |

---

## Authentification

Le backend utilise un systeme JWT custom :

1. **Login** : retourne un `access_token` (60 min) + `refresh_token` (30 jours)
2. **Requetes authentifiees** : header `Authorization: Bearer <access_token>`
3. **Refresh** : quand l'access token expire, envoyer le refresh token pour en obtenir un nouveau (rotation automatique)
4. **Logout** : revoque le refresh token en base

Les endpoints protege utilisent le middleware `get_current_user` (obligatoire) ou `get_optional_user` (pour les conversations).

---

## Codes de reponse

| Code | Signification |
|------|---------------|
| 200 | Succes |
| 201 | Ressource creee (booking, review, favorite) |
| 400 | Requete invalide (validation echouee) |
| 401 | Non authentifie |
| 403 | Acces interdit (pas proprietaire de la ressource) |
| 404 | Ressource non trouvee |
| 409 | Conflit (email deja pris, favori deja existant) |
| 503 | Service indisponible (Oracle deconnecte) |
