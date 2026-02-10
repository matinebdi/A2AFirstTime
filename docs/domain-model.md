# VacanceAI - Domain Model (DDD)

## Bounded Contexts

```
+---------------------+     +---------------------+     +---------------------+
|      Identity       |     |       Catalog        |     |    Hotel Discovery  |
|                     |     |                      |     |                     |
|  User               |     |  Destination         |     |  TripAdvisorLocation|
|  RefreshToken       |     |  Package             |     |  TripAdvisorPhoto   |
|  AccessToken (VO)   |     |  PackageIncludes(VO) |     |  TripAdvisorReview  |
+---------------------+     +---------------------+     +---------------------+
          |                           |
          |   +----------+            |
          +-->|  Booking  |<-----------+
          |   +----------+
          |
          |   +----------+
          +-->|  Social   |
              |           |
              |  Review   |
              |  Favorite |
              +----------+
                                     +---------------------+
                                     |    Conversation      |
                                     |                      |
                                     |  Conversation        |
                                     |  ChatMessage (VO)    |
                                     |  UIAction (VO)       |
                                     |  PageContext (VO)     |
                                     +---------------------+

                                     +---------------------+
                                     |    AI Agents         |
                                     |                      |
                                     |  Orchestrator        |
                                     |  UIAgent             |
                                     |  DatabaseAgent       |
                                     +---------------------+
```

## UML Class Diagram (Mermaid)

```mermaid
classDiagram
    direction TB

    %% ===== IDENTITY CONTEXT =====
    class User {
        <<Aggregate Root>>
        +String id
        +String email
        +String password_hash
        +String first_name
        +String last_name
        +String phone
        +String avatar_url
        +DateTime created_at
        +DateTime updated_at
    }

    class RefreshToken {
        <<Entity>>
        +String id
        +String token
        +DateTime expires_at
        +DateTime created_at
    }

    User "1" --> "0..*" RefreshToken : owns

    %% ===== CATALOG CONTEXT =====
    class Destination {
        <<Aggregate Root>>
        +String id
        +String name
        +String country
        +String city
        +String description
        +String image_url
        +String[] tags
        +Float average_rating
        +Int total_reviews
        +Float latitude
        +Float longitude
    }

    class Package {
        <<Aggregate Root>>
        +String id
        +String name
        +String description
        +Float price_per_person
        +Int duration_days
        +Int max_persons
        +String image_url
        +String[] images
        +Date available_from
        +Date available_to
        +Boolean is_active
        +Int hotel_category
        +checkAvailability(date, persons) Boolean
    }

    class PackageIncludes {
        <<Value Object>>
        +String transport
        +String hotel
        +String meals
        +String[] activities
        +String transfers
    }

    Destination "1" --> "0..*" Package : offers
    Package "1" *-- "1" PackageIncludes : includes

    %% ===== BOOKING CONTEXT =====
    class Booking {
        <<Aggregate Root>>
        +String id
        +Date start_date
        +Date end_date
        +Int num_persons
        +Float total_price
        +BookingStatus status
        +PaymentStatus payment_status
        +String special_requests
        +DateTime created_at
        +cancel() void
        +confirm() void
        +complete() void
    }

    class BookingStatus {
        <<Enumeration>>
        PENDING
        CONFIRMED
        CANCELLED
        COMPLETED
    }

    class PaymentStatus {
        <<Enumeration>>
        UNPAID
        PAID
        REFUNDED
    }

    User "1" --> "0..*" Booking : makes
    Package "1" --> "0..*" Booking : is booked as
    Booking --> BookingStatus
    Booking --> PaymentStatus

    %% ===== SOCIAL CONTEXT =====
    class Review {
        <<Entity>>
        +String id
        +Int rating
        +String comment
        +DateTime created_at
    }

    class Favorite {
        <<Entity>>
        +String id
        +DateTime created_at
    }

    User "1" --> "0..*" Review : writes
    User "1" --> "0..*" Favorite : saves
    Package "1" --> "0..*" Review : receives
    Package "1" --> "0..*" Favorite : is saved as
    Booking "0..1" --> "0..1" Review : leads to

    %% ===== CONVERSATION CONTEXT =====
    class Conversation {
        <<Aggregate Root>>
        +String id
        +DateTime created_at
        +DateTime updated_at
        +addMessage(role, content) void
    }

    class ChatMessage {
        <<Value Object>>
        +String role
        +String content
        +DateTime timestamp
        +UIAction[] ui_actions
    }

    class UIAction {
        <<Value Object>>
        +String action
        +Map~String, Any~ payload
    }

    class PageContext {
        <<Value Object>>
        +String page
        +String route
        +Map~String, Any~ data
    }

    User "0..1" --> "0..*" Conversation : participates in
    Conversation "1" *-- "0..*" ChatMessage : contains
    ChatMessage "1" *-- "0..*" UIAction : triggers
    Conversation ..> PageContext : receives with each message

    %% ===== HOTEL DISCOVERY CONTEXT =====
    class TripAdvisorLocation {
        <<Aggregate Root>>
        +String id
        +String location_id
        +String name
        +String description
        +Address address_obj
        +Float rating
        +Int num_reviews
        +String price_level
        +String search_country
    }

    class TripAdvisorPhoto {
        <<Entity>>
        +String id
        +String photo_id
        +String url_original
        +String url_large
        +String url_medium
        +String url_small
        +String caption
    }

    class TripAdvisorReview {
        <<Entity>>
        +String id
        +String review_id
        +String title
        +String text
        +Int rating
        +DateTime published_date
        +String username
    }

    TripAdvisorLocation "1" --> "0..*" TripAdvisorPhoto : has
    TripAdvisorLocation "1" --> "0..*" TripAdvisorReview : has

    %% ===== AI AGENTS CONTEXT =====
    class Orchestrator {
        <<Service>>
        +classifyRequest(message) AgentType
        +processRequest(message, context) Response
    }

    class UIAgent {
        <<Service>>
        +searchVacation(filters) PackageList
        +createBooking(details) Booking
        +showRecommendations(preferences) PackageList
        +navigateToPage(page) UIAction
    }

    class DatabaseAgent {
        <<Service>>
        +queryData(message) Result
    }

    Orchestrator --> UIAgent : routes to
    Orchestrator --> DatabaseAgent : routes to
    UIAgent ..> Package : searches
    UIAgent ..> Booking : creates
    UIAgent ..> Conversation : responds in
```

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

## Context Map (Relationships)

```
Identity ----[Customer/Supplier]----> Booking
Identity ----[Customer/Supplier]----> Social
Identity ----[Customer/Supplier]----> Conversation
Catalog  ----[Customer/Supplier]----> Booking
Catalog  ----[Customer/Supplier]----> Social
Conversation --[Conformist]---------> AI Agents
AI Agents ----[Anticorruption Layer]-> Catalog
AI Agents ----[Anticorruption Layer]-> Booking
Hotel Discovery --[Separate Ways]----> Catalog (no direct FK)
```
