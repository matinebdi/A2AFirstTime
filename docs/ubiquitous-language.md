# VacanceAI - Ubiquitous Language

A glossary of domain terms used throughout the codebase. All terms are defined in English with precise, unambiguous meanings.

---

## Core Domain

### User
A registered person who can browse packages, make bookings, leave reviews, and interact with the AI assistant. Identified by a unique UUID. Holds credentials (email + hashed password) and an optional profile (first name, last name, phone, avatar).

### Destination
A travel location defined by a name, country, and optional city. Each destination has descriptive tags (e.g. beach, mountain, city), an average rating computed from its packages' reviews, and geographic coordinates. There are 15 destinations in the system.

### Package
A purchasable vacation offer tied to a single destination. Defines a price per person, duration in days, maximum number of persons, availability window (available_from to available_to), hotel category (1-5 stars), and detailed contents (included services, not-included items, highlights). A package can be active or inactive.

### PackageIncludes
A value object describing what is included in a package: transport, hotel, meals, activities (list), and transfers.

### Booking
A reservation made by a user for a specific package. Records the start date, end date (computed from package duration), number of persons, total price (price_per_person x num_persons), optional special requests, and two statuses: booking status and payment status.

### BookingStatus
The lifecycle state of a booking. One of:
- **pending**: Booking has been created but not yet confirmed
- **confirmed**: Booking is confirmed by the system
- **cancelled**: Booking was cancelled by the user
- **completed**: The trip has been completed

### PaymentStatus
The payment state of a booking. One of:
- **unpaid**: No payment has been received
- **paid**: Payment has been received
- **refunded**: Payment has been returned to the user

### Favorite
A saved reference from a user to a package. Represents the user's intent to consider this package later. A user can have at most one favorite entry per package (unique constraint on user + package).

### Review
A rating and optional text comment left by a user for a package, optionally linked to a specific booking. The rating is an integer from 1 to 5.

---

## AI / Conversation Domain

### Conversation
A chat session between a user and the AI assistant. Contains an ordered list of messages and optional context metadata. Identified by a UUID. Persists across page navigations within the same session.

### ChatMessage
A single message within a conversation. Has a role (user or assistant), text content, a timestamp, and optional UI actions attached to assistant messages.

### UIAction
An instruction sent from the AI assistant to the frontend to trigger a visual action. Examples: navigate to a page, show search results as cards, open a booking form, display a booking confirmation.

### PageContext
Metadata describing what the user is currently viewing in the browser. Sent with every chat message to give the AI assistant awareness of the user's current page (route, displayed packages, bookings, etc.). Enables contextual references like "this one" or "the first result".

### Orchestrator
The top-level AI agent (LangGraph workflow) that receives a user message, classifies the intent, and routes it to the appropriate specialized agent (UI Agent or Database Agent).

### UIAgent
A ReAct-based AI agent (LangChain + Gemini) specialized in conversational vacation planning. Has access to tools for searching packages, showing details, creating bookings, adding favorites, navigating pages, and showing recommendations.

### DatabaseAgent
A specialized AI agent for direct database queries and reporting. Handles requests like data export, statistics, and raw data access.

---

## Hotel Discovery Domain

### TripAdvisorLocation
A hotel or accommodation sourced from TripAdvisor data. Contains name, address, geographic coordinates, phone, website, rating, number of reviews, ranking data, price level, and the country it was searched for.

### TripAdvisorPhoto
A photograph associated with a TripAdvisor location. Available in multiple resolutions (original, large, medium, small) with an optional caption.

### TripAdvisorReview
A guest review for a TripAdvisor location. Contains a title, text body, rating (1-5), publication date, travel date, trip type, and the reviewer's username and location.

---

## Authentication Domain

### AccessToken
A short-lived JWT token (default: 60 minutes) used to authenticate API requests. Contains the user's ID as the subject claim. Sent in the Authorization header as a Bearer token.

### RefreshToken
A long-lived token (default: 30 days) stored in the database, used to obtain a new access token without re-entering credentials. Rotated on each refresh (old token is invalidated, new one is issued).

---

## Infrastructure Terms

### Ingress
The Kubernetes NGINX reverse proxy that routes incoming HTTP requests to the appropriate service: `/api/*` to the backend, `/*` to the frontend.

### Checkpointer
An in-memory state store (LangGraph MemorySaver) that persists the AI agent's conversation state across multiple turns within the same conversation thread. Lost on pod restart.

### A2A (Agent-to-Agent)
A protocol for inter-agent communication. Defines an AgentCard (discovery), tasks with input/output, and state lifecycle (pending, running, completed, failed, cancelled).
