# Installation and Deployment - VacanceAI

---

## Prerequisites

- **Docker Desktop** (v24+) with **Kubernetes enabled** (Settings > Kubernetes > Enable)
- **kubectl** (included with Docker Desktop)
- **Git**
- **Python 3.12+** (for the seed script)

---

## Option A: Automated Setup (recommended)

```powershell
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

# Configure .env (see Configuration section)

.\setup.ps1
```

The `setup.ps1` script automatically executes:
1. Prerequisites check (Docker, kubectl, K8s, .env)
2. Oracle startup (docker compose) + healthcheck
3. Oracle schema initialization
4. Docker image builds (backend + frontend)
5. Ingress NGINX Controller v1.12.0 installation
6. K8s secrets generation from .env (base64)
7. Kubernetes manifest deployment
8. Pod readiness wait

Optional flags: `-SkipOracle`, `-SkipBuild`, `-SkipSchema`

---

## Option B: Manual Setup

### 1. Clone the Repository

```bash
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data
```

### 2. Install the Ingress NGINX Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 3. Start Oracle (Docker Compose)

```bash
docker compose up -d
```

Wait for Oracle to be healthy (~2 minutes on first launch):

```bash
docker compose ps   # oracle-xe should be "healthy"
```

### 4. Initialize the Oracle Schema

```bash
docker exec -i oracle-xe sqlplus SYS/admin@//localhost:1521/XE as SYSDBA < backend/database/oracle_schema.sql
```

### 5. Seed the Data

```bash
pip install oracledb requests
python scripts/seed_oracle.py
```

This inserts:
- 15 destinations (15 countries)
- 30 packages (2 per country: Explorer + Premium)
- 150 TripAdvisor hotels with photos and reviews

### 6. Build Docker Images

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
```

### 7. Deploy to Kubernetes

```bash
kubectl apply -f k8s/
```

Or step by step:

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### 8. Verify the Deployment

```bash
kubectl get pods -n vacanceai

# Expected output:
# NAME                        READY   STATUS    AGE
# backend-xxx                 1/1     Running   ...
# frontend-xxx                1/1     Running   ...
# jaeger-xxx                  1/1     Running   ...
```

---

## Configuration

### Environment Variables (.env)

Create a `.env` file at the project root:

```env
ORACLE_HOST=localhost
ORACLE_PORT=1521
ORACLE_SERVICE=XE
ORACLE_USER=VACANCEAI
ORACLE_PASSWORD=vacanceai

JWT_SECRET_KEY=your-secret-key-change-in-production
JWT_ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=60
REFRESH_TOKEN_EXPIRE_DAYS=30

GOOGLE_API_KEY=<your_gemini_key>
```

### Kubernetes Secrets (k8s/secrets.yaml)

Encode your values in base64 and add them to `k8s/secrets.yaml`:

```bash
echo -n "your-value" | base64
```

Required secrets:
- `ORACLE_PWD`: Oracle SYS password (default: `admin`)
- `ORACLE_PASSWORD`: VACANCEAI user password (default: `vacanceai`)
- `JWT_SECRET_KEY`: JWT secret key
- `GOOGLE_API_KEY`: Google Gemini API key

---

## Available URLs

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API | http://localhost/api/health |
| Swagger | http://localhost/swagger |
| ReDoc | http://localhost/redoc |
| Jaeger UI | http://localhost:31686 |
| Oracle | localhost:1521/XE |

---

## Useful Commands

### Docker Compose (Oracle)

```bash
docker compose up -d          # Start Oracle
docker compose down            # Stop Oracle
docker compose logs -f oracle  # Oracle logs
```

### Kubernetes (App)

```bash
kubectl get pods -n vacanceai                        # Pod status
kubectl logs -n vacanceai deploy/backend -f          # Backend logs
kubectl logs -n vacanceai deploy/frontend -f         # Frontend logs

# Rebuild + restart
docker build -t vacanceai-backend ./backend
kubectl rollout restart deploy/backend -n vacanceai

docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
kubectl rollout restart deploy/frontend -n vacanceai

# Health checks
curl http://localhost/api/health
curl http://localhost/api/ready

# Delete everything
kubectl delete -f k8s/
```

---

## Local Development (without Docker/K8s)

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Oracle must be running on localhost:1521
uvicorn api.main:app --reload --port 8000
# -> http://localhost:8000
```

### Frontend

```bash
cd frontend
npm install
npm run dev
# -> http://localhost:5173
```

---

## Logging

The backend has a centralized logging system that writes to `backend/log_apps/`.

| File | Content | Level |
|------|---------|-------|
| `app.log` | General application logs | INFO+ |
| `agents.log` | AI agent activity (orchestrator, UI, database) | DEBUG+ |
| `sql.log` | All SQL queries | DEBUG+ |
| `errors.log` | Errors from all loggers | ERROR+ |

- **Configuration**: `backend/logging_config.py` (`setup_logging()` called at FastAPI startup)
- **Rotation**: 5 MB max per file, 3 backups
- **K8s volume**: hostPath mounted from pod `/app/log_apps` to local `backend/log_apps/`

```bash
cat backend/log_apps/app.log      # General logs
cat backend/log_apps/sql.log      # SQL queries
cat backend/log_apps/agents.log   # AI agents
cat backend/log_apps/errors.log   # Errors
```

---

## Troubleshooting

### Backend not starting (readiness 503)

The readiness probe checks the Oracle connection. Verify Oracle is running:

```bash
docker compose ps   # oracle-xe should be "healthy"
```

### ErrImageNeverPull in K8s

Docker images don't exist locally. Build them first:

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
kubectl rollout restart deploy/backend deploy/frontend -n vacanceai
```

### Full Reset

```bash
kubectl delete -f k8s/
docker compose down
docker volume create oracle-xe-data
docker compose up -d
# Wait for healthy, then re-seed and re-deploy
```
