# API Endpoints - VacanceAI Backend

![API Endpoints Diagram](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-084040.png)

## Description

This diagram represents the 40 endpoints exposed by the VacanceAI FastAPI backend, organized into 9 routers. Each router corresponds to a file in `backend/api/routes/`.

---

## Overview

| Router | Prefix | Endpoints | Auth Required |
|--------|--------|-----------|---------------|
| Auth | `/api/auth` | 8 | Partial |
| Packages | `/api/packages` | 4 | No |
| Bookings | `/api/bookings` | 5 | Yes |
| Favorites | `/api/favorites` | 4 | Yes |
| Reviews | `/api/reviews` | 2 | Partial |
| Destinations | `/api/destinations` | 3 | No |
| Conversations | `/api/conversations` | 5 | Optional |
| TripAdvisor | `/api/tripadvisor` | 6 | No |
| Health | `/api` | 2 | No |
| **Total** | | **39 REST + 1 WebSocket** | |

---

## Auth (`backend/api/routes/auth.py`)

JWT authentication with refresh tokens.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| POST | `/api/auth/signup` | Register (email, password, first_name, last_name) | No |
| POST | `/api/auth/login` | Login -> access_token + refresh_token | No |
| POST | `/api/auth/logout` | Logout (revokes the refresh token) | Yes |
| POST | `/api/auth/refresh` | Token renewal (refresh token rotation) | No |
| GET | `/api/auth/me` | Current user profile | Yes |
| PATCH | `/api/auth/me` | Update profile (first_name, last_name, phone, avatar_url) | Yes |
| POST | `/api/auth/avatar` | Avatar upload (jpg/png/webp, max 2 MB) | Yes |
| GET | `/api/auth/avatar/{filename}` | Download an avatar | No |

---

## Packages (`backend/api/routes/packages.py`)

Vacation package catalog browsing.

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/packages` | List with filters | `destination`, `destination_id`, `min_price`, `max_price`, `min_duration`, `max_duration`, `tags`, `start_date`, `sort_by`, `limit`, `offset` |
| GET | `/api/packages/featured` | Popular packages | `limit` (1-20, default 6) |
| GET | `/api/packages/{id}` | Package details + destination + reviews | - |
| GET | `/api/packages/{id}/availability` | Availability check | `start_date` (required), `num_persons` (1-10) |

**Sort options** (`sort_by`): `price_asc`, `price_desc`, `duration_asc`, `duration_desc`, `name_asc`

---

## Bookings (`backend/api/routes/bookings.py`)

Booking management. All endpoints require authentication.

| Method | Endpoint | Description | Body |
|--------|----------|-------------|------|
| GET | `/api/bookings` | My bookings (with package + destination) | `status` (optional filter) |
| POST | `/api/bookings` | Create a booking | `package_id`, `start_date`, `num_persons`, `special_requests?` |
| GET | `/api/bookings/{id}` | Booking details | - |
| PATCH | `/api/bookings/{id}` | Update (status, special requests) | `status?`, `special_requests?` |
| DELETE | `/api/bookings/{id}` | Delete a booking | - |

---

## Favorites (`backend/api/routes/favorites.py`)

Favorites management. All endpoints require authentication.

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/favorites` | My favorites (with package + destination) |
| POST | `/api/favorites/{package_id}` | Add a package to favorites |
| DELETE | `/api/favorites/{package_id}` | Remove a package from favorites |
| GET | `/api/favorites/check/{package_id}` | Check if a package is favorited |

---

## Reviews (`backend/api/routes/reviews.py`)

Package reviews.

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/api/reviews/package/{package_id}` | Package reviews (with author info) | No |
| POST | `/api/reviews` | Submit a review (rating 1-5, comment) | Yes |

**GET parameters**: `limit` (1-50, default 10), `offset` (default 0)

---

## Destinations (`backend/api/routes/destinations.py`)

Destination browsing.

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/destinations` | List destinations | `country`, `tags` (comma-separated), `limit` (1-100, default 20) |
| GET | `/api/destinations/{id}` | Details + associated packages | - |
| GET | `/api/destinations/{id}/packages` | Packages for a destination | `min_price`, `max_price` |

---

## Conversations (`backend/api/routes/conversations.py`)

AI assistant chat. Authentication is optional (links conversation to user if logged in).

| Method | Endpoint | Description |
|--------|----------|-------------|
| **WS** | `/api/conversations/ws/{id}` | **WebSocket** real-time (message + page context) |
| POST | `/api/conversations/{id}/message` | Send a message (REST fallback) |
| GET | `/api/conversations/{id}` | Conversation history |
| DELETE | `/api/conversations/{id}` | Delete a conversation |
| POST | `/api/conversations/new` | Create a new conversation |

### WebSocket Format

**Send** (client -> server):
```json
{
  "message": "Book this one for 2 people",
  "context": {
    "user": {"id": "...", "email": "..."},
    "page": {"page": "package_detail", "data": {"package_id": "..."}}
  }
}
```

**Receive** (server -> client):
```json
{
  "response": "Booking confirmed!",
  "ui_actions": [{"action": "booking_confirmed", "data": {...}}],
  "agent_type": "ui",
  "timestamp": "2026-02-13T..."
}
```

---

## TripAdvisor (`backend/api/routes/tripadvisor.py`)

Hotel data imported from TripAdvisor.

| Method | Endpoint | Description | Parameters |
|--------|----------|-------------|------------|
| GET | `/api/tripadvisor/locations` | List hotels | `country` |
| GET | `/api/tripadvisor/locations-with-details` | Hotels + photos + reviews + average rating (optimized, single query) | `country` |
| GET | `/api/tripadvisor/countries` | List available countries | - |
| GET | `/api/tripadvisor/locations/{id}` | Hotel details | - |
| GET | `/api/tripadvisor/locations/{id}/photos` | Hotel photos | - |
| GET | `/api/tripadvisor/locations/{id}/reviews` | Hotel reviews | - |

**Note**: The `/locations-with-details` endpoint uses `joinedload()` to load photos and reviews in a single SQL query, avoiding N+1 queries.

---

## Health (`backend/api/routes/health.py`)

Kubernetes monitoring probes.

| Method | Endpoint | Description | Error Code |
|--------|----------|-------------|------------|
| GET | `/api/health` | Liveness probe (always 200) | - |
| GET | `/api/ready` | Readiness probe (checks Oracle connection) | 503 |

---

## Authentication

The backend uses a custom JWT system:

1. **Login**: returns an `access_token` (60 min) + `refresh_token` (30 days)
2. **Authenticated requests**: `Authorization: Bearer <access_token>` header
3. **Refresh**: when the access token expires, send the refresh token to get a new one (automatic rotation)
4. **Logout**: revokes the refresh token in the database

Protected endpoints use the `get_current_user` middleware (required) or `get_optional_user` (for conversations).

---

## Response Codes

| Code | Meaning |
|------|---------|
| 200 | Success |
| 201 | Resource created (booking, review, favorite) |
| 400 | Bad request (validation failed) |
| 401 | Unauthorized |
| 403 | Forbidden (not resource owner) |
| 404 | Resource not found |
| 409 | Conflict (email already taken, favorite already exists) |
| 503 | Service unavailable (Oracle disconnected) |
