# Justfile - Task automation for UI Automation A2A project

# Default recipe to display help
default:
    @just --list

# Start development environment with Docker Compose
dev:
    docker compose up --build

# Start in detached mode
dev-d:
    docker compose up --build -d

# Stop all services
stop:
    docker compose down

# Stop and remove volumes
clean:
    docker compose down -v
    rm -rf monitoring/prometheus/data monitoring/grafana/data

# Build all Docker images
build:
    docker compose build

# Rebuild specific service
rebuild service:
    docker compose build {{service}}
    docker compose up -d {{service}}

# View logs for a specific service
logs service:
    docker compose logs -f {{service}}

# View logs for all agents
logs-agents:
    docker compose logs -f orchestrator decision vision form validation

# Execute command in a running container
exec service cmd:
    docker compose exec {{service}} {{cmd}}

# Open shell in orchestrator
shell-orchestrator:
    docker compose exec orchestrator /bin/bash

# Open shell in frontend
shell-frontend:
    docker compose exec frontend /bin/sh

# Run backend tests
test-backend:
    docker compose exec orchestrator pytest tests/ -v

# Run frontend tests
test-frontend:
    docker compose exec frontend npm run test

# Run all tests
test:
    @just test-backend
    @just test-frontend

# Install frontend dependencies
install-frontend:
    cd frontend && npm install

# Database shell (PostgreSQL)
db-shell:
    docker compose exec postgres psql -U agent_user -d agent_memory

# Redis CLI
redis-cli:
    docker compose exec redis redis-cli

# Monitor Redis Pub/Sub messages (A2A protocol)
monitor-a2a:
    docker compose exec redis redis-cli PSUBSCRIBE "agent:*"

# Deploy to Kubernetes
deploy:
    kubectl apply -f deploy/infra/
    kubectl apply -f deploy/agents/
    kubectl apply -f deploy/gateway/
    kubectl apply -f deploy/monitoring/

# Delete Kubernetes deployment
undeploy:
    kubectl delete -f deploy/agents/
    kubectl delete -f deploy/gateway/
    kubectl delete -f deploy/monitoring/
    kubectl delete -f deploy/infra/

# Get Kubernetes pods status
k8s-status:
    kubectl get pods -n agents-system
    kubectl get pods -n agents-workers

# View Kubernetes logs for orchestrator
k8s-logs-orchestrator:
    kubectl logs -f -l app=orchestrator -n agents-workers

# View Kubernetes logs for decision agent
k8s-logs-decision:
    kubectl logs -f -l app=decision-agent -n agents-workers

# Port forward to Grafana
grafana:
    kubectl port-forward -n monitoring svc/grafana 3000:3000

# Port forward to Prometheus
prometheus:
    kubectl port-forward -n monitoring svc/prometheus 9090:9090

# Load test with k6 (if available)
load-test:
    docker run --rm -i --network=ui-automation-a2a_default \
      grafana/k6 run - < monitoring/k6/load-test.js

# Format Python code
format-python:
    docker compose exec orchestrator black app/
    docker compose exec decision black app/
    docker compose exec vision black app/
    docker compose exec form black app/
    docker compose exec validation black app/

# Format frontend code
format-frontend:
    cd frontend && npm run format

# Lint Python code
lint-python:
    docker compose exec orchestrator ruff check app/

# Lint frontend code
lint-frontend:
    cd frontend && npm run lint

# Check all code quality
check:
    @just lint-python
    @just lint-frontend

# Create Kubernetes secrets from .env file
create-secrets:
    kubectl create secret generic agent-secrets \
      --from-env-file=.env \
      -n agents-workers \
      --dry-run=client -o yaml | kubectl apply -f -

# Backup PostgreSQL database
backup-db:
    docker compose exec postgres pg_dump -U agent_user agent_memory > backup_$(date +%Y%m%d_%H%M%S).sql

# Restore PostgreSQL database from backup
restore-db backup_file:
    docker compose exec -T postgres psql -U agent_user agent_memory < {{backup_file}}

# View agent metrics (Prometheus query)
metrics:
    curl -s http://localhost:9090/api/v1/query?query=a2a_messages_total | jq

# Health check all services
health:
    @echo "Checking Orchestrator..."
    @curl -s http://localhost:8000/health || echo "❌ Orchestrator down"
    @echo "\nChecking Frontend..."
    @curl -s http://localhost:5173 > /dev/null && echo "✅ Frontend up" || echo "❌ Frontend down"
    @echo "\nChecking Redis..."
    @docker compose exec redis redis-cli ping || echo "❌ Redis down"
    @echo "\nChecking PostgreSQL..."
    @docker compose exec postgres pg_isready -U agent_user || echo "❌ PostgreSQL down"

# Show resource usage
stats:
    docker stats --no-stream

# Restart specific service
restart service:
    docker compose restart {{service}}

# Preview production build locally
preview:
    docker compose -f compose.yaml -f compose.production.yaml up --build

# Initialize project (first time setup)
init:
    @echo "🚀 Initializing UI Automation A2A project..."
    @cp .env.example .env 2>/dev/null || echo "⚠️  Create .env file manually"
    @just install-frontend
    @echo "✅ Project initialized! Run 'just dev' to start."
