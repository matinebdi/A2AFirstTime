# VacanceAI - Modele de Domaine (DDD)

## Diagramme UML des Classes

![Diagramme UML Classes](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090534.png)

---

## Context Map

![Context Map](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-091721.png)

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

## Aggregats

| Aggregate Root | Entites / Value Objects | Invariants |
|----------------|------------------------|------------|
| **User** | RefreshToken | Email unique. Mot de passe hashe (bcrypt). |
| **Destination** | tags (JSON) | Pays obligatoire. Rating calcule depuis les avis des packages. |
| **Package** | PackageIncludes (VO) | Prix > 0. Duree > 0. available_from < available_to. |
| **Booking** | BookingStatus (enum), PaymentStatus (enum) | num_persons <= package.max_persons. total_price = prix x nombre. |
| **Review** | - | Rating entre 1 et 5. Un seul avis par utilisateur par reservation. |
| **Favorite** | - | Contrainte d'unicite sur (user_id, package_id). |
| **Conversation** | ChatMessage (VO), UIAction (VO), PageContext (VO) | Messages en append-only et ordonnes. |
| **TripAdvisorLocation** | TripAdvisorPhoto, TripAdvisorReview | location_id unique (identifiant externe). |

---

## Relations entre Contexts

| Source | Relation | Target | Description |
|--------|----------|--------|-------------|
| Identity | Customer/Supplier | Booking | Identity fournit les utilisateurs aux reservations |
| Identity | Customer/Supplier | Social | Identity fournit les utilisateurs aux avis et favoris |
| Identity | Customer/Supplier | Conversation | Identity fournit les utilisateurs au chat |
| Catalog | Customer/Supplier | Booking | Catalog fournit les packages aux reservations |
| Catalog | Customer/Supplier | Social | Catalog fournit les packages aux avis et favoris |
| Conversation | Conformist | AI Agents | Conversation se conforme au format des agents IA |
| AI Agents | Anticorruption Layer | Catalog | Les agents accedent au catalogue via une couche d'abstraction |
| AI Agents | Anticorruption Layer | Booking | Les agents accedent aux reservations via une couche d'abstraction |
| Hotel Discovery | Separate Ways | Catalog | Pas de FK directe, donnees independantes |
