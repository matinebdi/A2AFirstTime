# Agent IA et PageContext - VacanceAI

![Diagramme Agent IA](sc/Mermaid%20Chart%20-%20Create%20complex,%20visual%20diagrams%20with%20text.-2026-02-13-090149.png)

L'assistant IA de VacanceAI est propulse par Google Gemini 2.0 Flash et orchestre via LangChain + LangGraph. Il est context-aware : il connait la page que l'utilisateur consulte et les donnees affichees.

---

## Architecture des agents

### Orchestrateur (`agents/orchestrator/agent.py`)
Agent coordinateur LangGraph qui recoit les messages utilisateur et les route vers l'agent le plus adapte :
- **UI Agent** : pour les actions d'interface (recherche, reservation, navigation)
- **Database Agent** : pour les requetes de donnees complexes

### UI Agent (`agents/ui/agent.py`)
Agent ReAct avec checkpointer en memoire (MemorySaver). Il utilise Gemini pour comprendre les demandes et appeler les outils adaptes. Le checkpointer maintient le contexte de conversation (perdu au redemarrage du pod).

### Database Agent (`agents/database/agent.py`)
Agent specialise pour les requetes Oracle via des tools LangChain.

---

## Outils de l'agent UI

| Outil | Description |
|-------|-------------|
| `search_vacation` | Rechercher des packages avec filtres (destination, prix, duree) |
| `show_package_details` | Afficher les details d'un package specifique |
| `create_booking_action` | Creer une reservation directement |
| `start_booking_flow` | Ouvrir le formulaire de reservation sur un package |
| `add_to_favorites_action` | Ajouter un package aux favoris |
| `navigate_to_page` | Naviguer le frontend vers une page |
| `show_recommendations` | Afficher des recommandations personnalisees |

Les outils qui retournent une cle `action` declenchent une action UI dans le frontend (navigation, affichage de cartes, etc.).

---

## PageContext System

### Fonctionnement

1. **`PageContext`** (React Context) stocke les informations de la page courante
2. Chaque page met a jour ce contexte via `useSetPageContext()` dans un `useEffect`
3. **`ChatWidget`** lit `usePageContext()` et l'envoie avec chaque message WebSocket
4. Le backend (orchestrateur) extrait `context.get("page")` et le passe a l'agent UI
5. L'agent UI ajoute `[Page actuelle: {...}]` au `HumanMessage`
6. L'agent utilise ces donnees pour resoudre les references implicites ("celui-ci", "le premier", "ma derniere reservation")

### Donnees envoyees par page

| Page | Donnees |
|------|---------|
| Home | `featured_packages: [{id, name}]` |
| Search | `filters: {destination, min_price, ...}`, `results: [{id, name, price}]` |
| PackageDetail | `package_id, package_name, destination, price, duration` |
| Bookings | `bookings: [{id, package_name, status, start_date}]` |
| Hotels | `hotels: [{location_id, name, country, rating}]` |
| HotelDetail | `location_id, hotel_name, country, rating` |

### Exemples d'utilisation

- Sur **PackageDetail** : "reserve celui-ci pour 2 personnes le 15 juin" -> l'agent connait le package affiche
- Sur **Search** : "montre-moi plus de details sur le premier" -> l'agent connait les resultats de recherche
- Sur **Bookings** : "annule ma derniere reservation" -> l'agent voit la liste des reservations

---

## Navigation automatique apres action

Quand l'agent effectue certaines actions, le `ChatWidget` navigue automatiquement l'utilisateur vers la page pertinente :

| Action agent | Navigation automatique |
|-------------|----------------------|
| Reservation confirmee (`booking_confirmed`) | `/bookings` |
| Ajout aux favoris (`add_favorite`) | `/favorites` |

Apres `add_favorite`, le ChatWidget appelle aussi `favoritesApi.add()` pour persister le favori cote client avant de naviguer.

---

## Format des messages WebSocket

### Envoi (client -> serveur)

```json
{
  "message": "Reserve celui-ci pour 2 personnes le 15 juin",
  "context": {
    "user": {"id": "abc-123", "email": "user@example.com"},
    "page": {
      "page": "package_detail",
      "data": {
        "package_id": "pkg-456",
        "package_name": "Bali Explorer",
        "destination": "Indonesie",
        "price": 1299.99,
        "duration": 7
      }
    }
  }
}
```

### Reception (serveur -> client)

```json
{
  "response": "Reservation confirmee pour 2 personnes le 15 juin !",
  "ui_actions": [
    {
      "action": "booking_confirmed",
      "data": {"booking_id": "book-789", "package_name": "Bali Explorer"}
    }
  ],
  "agent_type": "ui",
  "timestamp": "2026-02-13T10:30:00Z"
}
```

---

## Fichiers cles

| Fichier | Description |
|---------|-------------|
| `backend/agents/base.py` | Configuration LLM (Gemini 2.0 Flash) |
| `backend/agents/orchestrator/agent.py` | Orchestrateur LangGraph |
| `backend/agents/ui/agent.py` | Agent UI (ReAct + MemorySaver) |
| `backend/agents/ui/tools.py` | Outils UI (search, book, navigate, etc.) |
| `backend/agents/database/agent.py` | Agent Database |
| `backend/agents/database/tools.py` | Outils DB (search, booking, favorites) |
| `frontend/src/contexts/PageContext.tsx` | React Context pour la page courante |
| `frontend/src/components/chat/ChatWidget.tsx` | Widget de chat (WebSocket + PageContext) |
| `backend/api/routes/conversations.py` | Route WebSocket + REST pour le chat |
