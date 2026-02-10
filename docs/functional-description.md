# VacanceAI - Functional Description

## What is VacanceAI?

VacanceAI is a vacation booking platform enhanced with an AI-powered conversational assistant. It allows travelers to discover destinations, browse vacation packages, make reservations, and get personalized recommendations through natural language interaction.

## User Needs

### 1. Discover Vacation Destinations
A traveler wants to explore available destinations across 15 countries, compare options by rating, tags (beach, mountain, city, adventure, romantic, family), and find a place that matches their preferences.

### 2. Browse and Compare Packages
A traveler wants to view detailed vacation packages for a given destination, including price per person, duration, included services (transport, hotel, meals, activities, transfers), highlights, and availability dates. They need to compare packages side-by-side to make an informed decision.

### 3. Book a Vacation
A registered traveler wants to reserve a vacation package for a specific date and number of persons. The system calculates the total price, records the booking with a pending status, and allows the user to track its lifecycle (pending, confirmed, cancelled, completed).

### 4. Manage Bookings
A traveler wants to view all their bookings, check statuses, and cancel a reservation if plans change.

### 5. Save Favorites
A traveler wants to save interesting packages for later without committing to a booking. They can add or remove packages from their favorites list at any time.

### 6. Leave Reviews
After a trip, a traveler wants to rate and review a package (1-5 stars + comment) to help other travelers decide. Reviews are linked to a specific booking.

### 7. Get AI-Powered Assistance
A traveler wants to interact with a conversational AI assistant that can:
- Understand natural language requests in French or English ("Je cherche une plage pas chere pour 2 personnes")
- Search packages based on described preferences (destination, budget, duration, travel type)
- Show detailed package information within the chat
- Create a booking directly through the conversation
- Navigate the user to relevant pages
- Provide personalized recommendations based on preferences and budget range
- Understand what the user is currently viewing on the page (page context awareness) and resolve references like "this one", "the first one", "my last booking"

### 8. Explore Hotels (TripAdvisor Integration)
A traveler wants to browse hotel information sourced from TripAdvisor for their chosen destination, including photos, ratings, and guest reviews.

### 9. Secure Account Management
A traveler wants to create an account, log in securely, manage their profile (name, phone, avatar), and have their session persist across visits via refresh tokens.

### 10. Automated Deployment
A developer wants to deploy the full stack (Oracle database, backend, frontend, Kubernetes) with a single command (`setup.ps1`). The script handles prerequisites check, database startup, schema initialization, Docker image builds, Ingress controller installation, secrets generation, and K8s deployment.

### 11. Application Logging and Debugging
A developer wants to monitor application health and debug issues through centralized log files. Four rotating log files (app, agents, sql, errors) are written to `backend/log_apps/` and mounted to the local repo via a Kubernetes hostPath volume for real-time access.

## Key User Flows

### Flow 1: Search and Book via UI
1. User visits the home page and sees featured packages
2. User navigates to the search page and applies filters (destination, price, duration)
3. User clicks on a package to view details (included services, highlights, reviews)
4. User fills in the booking form (date, number of persons, special requests)
5. System confirms the booking with total price

### Flow 2: Book via AI Chatbot
1. User opens the chat widget from any page
2. User describes what they want: "I want a beach vacation for 2 people under 1500 euros"
3. AI assistant searches packages matching the criteria and displays cards in the chat
4. User selects a package: "book the first one for March 15th"
5. AI creates the booking directly and shows a confirmation
6. User is automatically redirected to the bookings page

### Flow 3: Contextual AI Assistance
1. User is viewing a specific package detail page
2. User opens the chat and asks "Can you book this one for next week?"
3. AI reads the page context, identifies the displayed package, and creates the booking
