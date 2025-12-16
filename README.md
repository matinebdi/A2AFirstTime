# UI Automation A2A - Multi-Agent Workflow Engine

![License](https://img.shields.io/badge/license-MIT-blue.svg)
![Python](https://img.shields.io/badge/python-3.12-blue.svg)
![React](https://img.shields.io/badge/react-19-blue.svg)
![Kubernetes](https://img.shields.io/badge/kubernetes-ready-green.svg)

A production-ready multi-agent system using Google's **Agent-to-Agent (A2A)** protocol for intelligent UI automation and testing, deployed on Kubernetes with comprehensive monitoring.

## 🎯 Project Overview

This project demonstrates a modern microservices architecture where AI agents collaborate to automate user interface interactions. Agents communicate using the A2A protocol, making decisions, analyzing UI elements, and executing actions autonomously.

### Key Features

- 🤖 **5 Specialized Agents**: Orchestrator, Decision, Vision, Form, Validation
- 🔄 **A2A Protocol**: Structured agent-to-agent communication via Redis Pub/Sub
- 🧠 **AI-Powered**: Google Gemini integration for intelligent decision-making
- 📊 **Real-time Dashboard**: React-based visualization of agent activity
- ☸️ **Kubernetes Native**: Full K8s deployment with auto-scaling
- 📈 **Complete Monitoring**: Prometheus, Grafana, and OpenTelemetry
- 🔒 **Secure**: JWT authentication, secrets management
- 🚀 **CI/CD Ready**: GitHub Actions pipeline

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                        Frontend (React)                      │
│              WebSocket + Agent Visualization                 │
└────────────────────┬────────────────────────────────────────┘
                     │
                     ▼
┌─────────────────────────────────────────────────────────────┐
│                    API Gateway (Envoy)                       │
└────────────────────┬────────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        ▼                         ▼
┌──────────────┐          ┌──────────────┐
│ Orchestrator │◄────────►│    Redis     │
│    Agent     │          │  (Pub/Sub)   │
└──────┬───────┘          └──────────────┘
       │
       ├─► Decision Agent (Gemini AI)
       │
       ├─► Vision Agent (UI Analysis)
       │
       ├─► Form Agent (Data + Memory)
       │
       └─► Validation Agent (Verification)
              │
              ▼
       ┌──────────────┐
       │  PostgreSQL  │
       │   (Memory)   │
       └──────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 20+
- Python 3.12+
- kubectl (for K8s deployment)
- Just (command runner) - `cargo install just`

### Local Development

```bash
# Clone the repository
git clone <your-repo-url>
cd ui-automation-a2a

# Start all services
just dev

# Access the application
# Frontend: http://localhost:5173
# Backend API: http://localhost:8000
# Grafana: http://localhost:3000
```

### Environment Setup

Create `.env` file in the root:

```env
# Database
POSTGRES_USER=agent_user
POSTGRES_PASSWORD=agent_password
POSTGRES_DB=agent_memory

# Redis
REDIS_HOST=redis
REDIS_PORT=6379

# AI Services
GOOGLE_API_KEY=your_gemini_api_key_here

# Security
JWT_SECRET=your_jwt_secret_here
```

## 📦 Project Structure

```
ui-automation-a2a/
├── agents/                    # Microservices agents
│   ├── orchestrator/         # Main coordinator
│   ├── decision/             # AI decision maker
│   ├── vision/               # UI analyzer
│   ├── form/                 # Form handler with memory
│   └── validation/           # Result validator
├── shared/                   # Shared libraries
│   └── a2a_protocol/        # A2A message schemas
├── frontend/                 # React dashboard
│   ├── src/
│   │   ├── components/      # UI components
│   │   └── hooks/           # Custom hooks
├── deploy/                   # Kubernetes manifests
│   ├── agents/              # Agent deployments
│   ├── infra/               # Infrastructure (Redis, PostgreSQL)
│   ├── monitoring/          # Prometheus, Grafana
│   └── gateway/             # Envoy Gateway
├── monitoring/              # Monitoring configs
├── .github/workflows/       # CI/CD pipelines
├── compose.yaml            # Docker Compose dev
├── Justfile                # Task automation
└── README.md
```

## 🤖 Agent Overview

### Orchestrator Agent
- Receives UI events from frontend
- Dispatches tasks to specialized agents
- Coordinates A2A message flow
- No decision-making, pure coordination

### Decision Agent
- Analyzes context and state
- Creates action plans using Gemini AI
- Decides which agents to invoke
- Maintains decision history

### Vision Agent
- Analyzes screenshots and UI elements
- Detects buttons, forms, and interactive elements
- Uses Gemini Vision for understanding

### Form Agent
- Fills form fields intelligently
- Stores user data in PostgreSQL
- Retrieves historical form data

### Validation Agent
- Verifies action success
- Checks UI state changes
- Reports results to orchestrator

## 🔄 A2A Protocol

### Message Structure

```json
{
  "message_id": "uuid-v4",
  "from_agent": "orchestrator",
  "to_agent": "decision",
  "message_type": "request|response|event",
  "timestamp": "2025-12-16T10:30:00Z",
  "payload": {
    "task": "analyze_context",
    "context": {},
    "priority": "high|normal|low"
  },
  "callback_id": "parent-message-uuid",
  "correlation_id": "workflow-uuid"
}
```

### Communication Flow

1. **User Action** → Frontend sends event via WebSocket
2. **Orchestrator** receives and creates A2A request
3. **Decision Agent** analyzes and plans actions
4. **Specialized Agents** execute tasks in parallel/sequence
5. **Orchestrator** aggregates responses
6. **Frontend** displays real-time updates

## ☸️ Kubernetes Deployment

```bash
# Deploy to Kubernetes
just deploy

# Check status
kubectl get pods -n agents-system

# View logs
just logs orchestrator

# Scale decision agent
kubectl scale deployment decision-agent --replicas=5 -n agents-workers
```

### Auto-scaling

Horizontal Pod Autoscaler (HPA) configured for:
- Decision Agent: 1-5 replicas (CPU 50%)
- Vision Agent: 1-5 replicas (CPU 50%)
- Form Agent: 2-4 replicas (CPU 60%)

## 📊 Monitoring

### Prometheus Metrics

```
# A2A Messages
a2a_messages_total{from_agent, to_agent}
a2a_message_latency_seconds{from_agent, to_agent}

# Agent Performance
agent_task_duration_seconds{agent, task}
agent_errors_total{agent, error_type}

# System
redis_pubsub_messages_total
postgres_connections_active
```

### Grafana Dashboards

Access: http://localhost:3000 (user: admin, pass: admin)

- **Agent Activity**: Real-time agent communication
- **A2A Message Flow**: Protocol metrics
- **System Health**: Resource usage
- **Workflow Timeline**: End-to-end traces

## 🧪 Testing

```bash
# Backend tests
cd agents/orchestrator
pytest tests/

# Frontend tests
cd frontend
npm run test

# Load testing
just load-test
```

## 🎬 Demo Scenarios

### Scenario 1: Auto-Fill Registration Form

1. User clicks "Auto-Fill" button
2. Orchestrator receives event
3. Decision Agent plans: "Fill username, email, password"
4. Form Agent retrieves or generates data
5. Vision Agent validates form state
6. Validation Agent confirms success

### Scenario 2: Multi-Step Checkout

1. User initiates checkout
2. Agents collaborate to:
   - Fill shipping address
   - Select payment method
   - Review order
   - Confirm purchase
3. Dashboard shows agent collaboration in real-time

## 📚 Documentation

- [A2A Protocol Specification](./docs/A2A_PROTOCOL.md)
- [Agent Development Guide](./docs/AGENT_DEVELOPMENT.md)
- [Kubernetes Deployment](./docs/KUBERNETES.md)
- [Monitoring Setup](./docs/MONITORING.md)

## 🛠️ Available Commands (Justfile)

```bash
just dev          # Start development environment
just build        # Build all Docker images
just deploy       # Deploy to Kubernetes
just logs <svc>   # View service logs
just test         # Run all tests
just clean        # Stop and remove all containers
just monitor      # Open Grafana dashboard
```

## 🤝 Contributing

This is an educational project for learning A2A protocol and Kubernetes. Feel free to explore and adapt!

## 📝 License

MIT License - see LICENSE file for details

## 🙏 Acknowledgments

- Google Gemini AI for intelligent decision-making
- Kubernetes community for excellent documentation
- FastAPI for modern Python web framework

---

**Built with ❤️ for learning Agent-to-Agent protocols and Kubernetes orchestration**
