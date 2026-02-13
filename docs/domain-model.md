# VacanceAI - Domain Model (DDD)

## UML Class Diagram

![UML Class Diagram](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090534.png)

---

## Context Map

![Context Map](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-091721.png)

---

## Bounded Contexts

| Context | Entities | Description |
|---------|----------|-------------|
| **Identity** | User, RefreshToken, AccessToken (VO) | User management and authentication |
| **Catalog** | Destination, Package, PackageIncludes (VO) | Destination and vacation package catalog |
| **Booking** | Booking, BookingStatus (enum), PaymentStatus (enum) | Reservations and payments |
| **Social** | Review, Favorite | User reviews and favorites |
| **Conversation** | Conversation, ChatMessage (VO), UIAction (VO), PageContext (VO) | AI chat with page context awareness |
| **Hotel Discovery** | TripAdvisorLocation, TripAdvisorPhoto, TripAdvisorReview | TripAdvisor hotel data |
| **AI Agents** | Orchestrator, UIAgent, DatabaseAgent | AI agents (LangGraph + LangChain) |

---

## Aggregates

| Aggregate Root | Entities / Value Objects | Invariants |
|----------------|------------------------|------------|
| **User** | RefreshToken | Email must be unique. Password is hashed (bcrypt). |
| **Destination** | tags (JSON) | Country is required. Rating is computed from package reviews. |
| **Package** | PackageIncludes (VO) | Price > 0. Duration > 0. available_from < available_to. |
| **Booking** | BookingStatus (enum), PaymentStatus (enum) | num_persons <= package.max_persons. total_price = price x count. |
| **Review** | - | Rating between 1 and 5. One review per user per booking. |
| **Favorite** | - | Unique constraint on (user_id, package_id). |
| **Conversation** | ChatMessage (VO), UIAction (VO), PageContext (VO) | Messages are append-only and ordered. |
| **TripAdvisorLocation** | TripAdvisorPhoto, TripAdvisorReview | location_id is unique (external identifier). |

---

## Context Map Relationships

| Source | Relation | Target | Description |
|--------|----------|--------|-------------|
| Identity | Customer/Supplier | Booking | Identity provides users to the booking context |
| Identity | Customer/Supplier | Social | Identity provides users to reviews and favorites |
| Identity | Customer/Supplier | Conversation | Identity provides users to the chat context |
| Catalog | Customer/Supplier | Booking | Catalog provides packages to bookings |
| Catalog | Customer/Supplier | Social | Catalog provides packages to reviews and favorites |
| Conversation | Conformist | AI Agents | Conversation conforms to the AI agents' message format |
| AI Agents | Anticorruption Layer | Catalog | Agents access the catalog through an abstraction layer |
| AI Agents | Anticorruption Layer | Booking | Agents access bookings through an abstraction layer |
| Hotel Discovery | Separate Ways | Catalog | No direct FK, independent data |
