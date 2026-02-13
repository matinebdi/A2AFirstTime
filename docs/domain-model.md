# VacanceAI - Domain Model (DDD)

## UML Class Diagram

![Diagramme UML Classes](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090534.png)

---

## Bounded Contexts

| Context | Entites | Description |
|---------|---------|-------------|
| **Identity** | User, RefreshToken, AccessToken (VO) | Gestion des utilisateurs et authentification |
| **Catalog** | Destination, Package, PackageIncludes (VO) | Catalogue de destinations et packages vacances |
| **Booking** | Booking, BookingStatus (enum), PaymentStatus (enum) | Reservations et paiements |
| **Social** | Review, Favorite | Avis et favoris utilisateurs |
| **Conversation** | Conversation, ChatMessage (VO), UIAction (VO), PageContext (VO) | Chat IA avec contexte de page |
| **Hotel Discovery** | TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview | Donnees hotels TripAdvisor |
| **AI Agents** | Orchestrator, UIAgent, DatabaseAgent | Agents IA (LangGraph + LangChain) |

---

## Aggregate Boundaries

| Aggregate Root       | Owned Entities / Value Objects                        | Invariants                                                     |
|----------------------|-------------------------------------------------------|----------------------------------------------------------------|
| **User**             | RefreshToken                                          | Email must be unique. Password is hashed (bcrypt).             |
| **Destination**      | (tags as JSON)                                        | Country is required. Rating is computed from package reviews.  |
| **Package**          | PackageIncludes (VO)                                  | Price > 0. Duration > 0. available_from < available_to.        |
| **Booking**          | BookingStatus (enum), PaymentStatus (enum)            | num_persons <= package.max_persons. total_price = price x num. |
| **Review**           | -                                                     | Rating between 1 and 5. One review per user per booking.       |
| **Favorite**         | -                                                     | Unique constraint on (user_id, package_id).                    |
| **Conversation**     | ChatMessage (VO), UIAction (VO), PageContext (VO)     | Messages are append-only and ordered.                          |
| **TripAdvisorLocation** | TripAdvisorPhoto, TripAdvisorReview                | location_id is unique (external identifier).                   |

---

## Context Map (Relationships)

| Source | Relation | Target |
|--------|----------|--------|
| Identity | Customer/Supplier | Booking |
| Identity | Customer/Supplier | Social |
| Identity | Customer/Supplier | Conversation |
| Catalog | Customer/Supplier | Booking |
| Catalog | Customer/Supplier | Social |
| Conversation | Conformist | AI Agents |
| AI Agents | Anticorruption Layer | Catalog |
| AI Agents | Anticorruption Layer | Booking |
| Hotel Discovery | Separate Ways | Catalog (no direct FK) |
