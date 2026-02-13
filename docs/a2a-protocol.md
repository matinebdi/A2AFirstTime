# Protocole Agent-to-Agent (A2A) - VacanceAI

Le backend utilise le protocole Agent-to-Agent (A2A) de Google pour la coordination des agents IA.

---

## Agents

| Agent | Role | Technologie |
|-------|------|-------------|
| **Orchestrator** | Coordonne les autres agents, route les messages | LangGraph |
| **Database** | Execute les requetes Oracle | LangChain tools |
| **UI** | Actions d'interface utilisateur (recherche, reservation, navigation) | ReAct + MemorySaver |

---

## Endpoints A2A

| Methode | Endpoint | Description |
|---------|----------|-------------|
| GET | `/.well-known/agent.json` | Agent Card (metadonnees de l'agent) |
| POST | `/a2a/tasks` | Creer une nouvelle tache |
| GET | `/a2a/tasks/{id}` | Recuperer le statut d'une tache |
| POST | `/a2a/tasks/{id}/messages` | Envoyer un message a une tache |
| POST | `/a2a/tasks/{id}/cancel` | Annuler une tache en cours |

---

## Agent Card

L'Agent Card est un document JSON expose a `/.well-known/agent.json` qui decrit les capacites de l'agent :

```json
{
  "name": "VacanceAI Assistant",
  "description": "Assistant IA pour la reservation de vacances",
  "capabilities": ["search", "booking", "navigation", "recommendations"],
  "protocol_version": "1.0"
}
```

---

## Flux de communication

```
Utilisateur
    │
    ▼
WebSocket (/api/conversations/ws/{id})
    │
    ▼
Orchestrator (LangGraph)
    ├──► UI Agent ──► Tools (search, book, navigate...)
    │                   │
    │                   ▼
    │               Actions UI -> Frontend
    │
    └──► Database Agent ──► Tools (query Oracle)
                              │
                              ▼
                          Oracle 21c XE
```

1. Le message utilisateur arrive via WebSocket
2. L'orchestrateur classifie le message et le route vers l'agent adapte
3. L'agent execute ses outils et retourne une reponse
4. Les `ui_actions` sont renvoyees au frontend pour execution

---

## Fichiers

| Fichier | Description |
|---------|-------------|
| `backend/a2a/protocol.py` | Schemas Pydantic du protocole A2A |
| `backend/a2a/client.py` | Client A2A (pour appeler d'autres agents) |
| `backend/a2a/server.py` | Serveur A2A (expose les endpoints) |
