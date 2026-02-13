# Installation et Deploiement - VacanceAI

---

## Prerequis

- **Docker Desktop** (v24+) avec **Kubernetes active** (Settings > Kubernetes > Enable)
- **kubectl** (inclus avec Docker Desktop)
- **Git**
- **Python 3.12+** (pour le script de seed)

---

## Option A : Setup automatique (recommande)

```powershell
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data

# Configurer .env (voir section Configuration)

.\setup.ps1
```

Le script `setup.ps1` execute automatiquement :
1. Verification des prerequis (Docker, kubectl, K8s, .env)
2. Demarrage Oracle (docker compose) + healthcheck
3. Initialisation du schema Oracle
4. Build des images Docker (backend + frontend)
5. Installation Ingress NGINX Controller v1.12.0
6. Generation des secrets K8s depuis .env (base64)
7. Deploiement des manifests Kubernetes
8. Attente que les pods soient Ready

Flags optionnels : `-SkipOracle`, `-SkipBuild`, `-SkipSchema`

---

## Option B : Setup manuel

### 1. Cloner le repository

```bash
git clone https://github.com/matinebdi/A2AFirstTime.git
cd A2AFirstTime
docker volume create oracle-xe-data
```

### 2. Installer l'Ingress NGINX Controller

```bash
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml

kubectl wait --namespace ingress-nginx \
  --for=condition=ready pod \
  --selector=app.kubernetes.io/component=controller \
  --timeout=120s
```

### 3. Demarrer Oracle (Docker Compose)

```bash
docker compose up -d
```

Attendre qu'Oracle soit healthy (~2 minutes au premier lancement) :

```bash
docker compose ps   # oracle-xe doit etre "healthy"
```

### 4. Initialiser le schema Oracle

```bash
docker exec -i oracle-xe sqlplus SYS/admin@//localhost:1521/XE as SYSDBA < backend/database/oracle_schema.sql
```

### 5. Seed les donnees

```bash
pip install oracledb requests
python scripts/seed_oracle.py
```

Cela insere :
- 15 destinations (15 pays)
- 30 packages (2 par pays : Explorer + Premium)
- 150 hotels TripAdvisor avec photos et avis

### 6. Builder les images Docker

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
```

### 7. Deployer sur Kubernetes

```bash
kubectl apply -f k8s/
```

Ou etape par etape :

```bash
kubectl apply -f k8s/namespace.yaml
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml
kubectl apply -f k8s/jaeger.yaml
kubectl apply -f k8s/backend.yaml
kubectl apply -f k8s/frontend.yaml
kubectl apply -f k8s/ingress.yaml
```

### 8. Verifier le deploiement

```bash
kubectl get pods -n vacanceai

# Resultat attendu :
# NAME                        READY   STATUS    AGE
# backend-xxx                 1/1     Running   ...
# frontend-xxx                1/1     Running   ...
# jaeger-xxx                  1/1     Running   ...
```

---

## Configuration

### Variables d'environnement (.env)

Creer un fichier `.env` a la racine du projet :

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

GOOGLE_API_KEY=<votre_cle_gemini>
```

### Secrets Kubernetes (k8s/secrets.yaml)

Encoder vos valeurs en base64 et les mettre dans `k8s/secrets.yaml` :

```bash
echo -n "votre-valeur" | base64
```

Secrets requis :
- `ORACLE_PWD` : mot de passe SYS Oracle (default: `admin`)
- `ORACLE_PASSWORD` : mot de passe user VACANCEAI (default: `vacanceai`)
- `JWT_SECRET_KEY` : cle secrete JWT
- `GOOGLE_API_KEY` : cle API Google Gemini

---

## URLs disponibles

| Service | URL |
|---------|-----|
| Frontend | http://localhost |
| API | http://localhost/api/health |
| Swagger | http://localhost/swagger |
| ReDoc | http://localhost/redoc |
| Jaeger UI | http://localhost:31686 |
| Oracle | localhost:1521/XE |

---

## Commandes utiles

### Docker Compose (Oracle)

```bash
docker compose up -d          # Demarrer Oracle
docker compose down            # Arreter Oracle
docker compose logs -f oracle  # Logs Oracle
```

### Kubernetes (App)

```bash
kubectl get pods -n vacanceai                        # Etat des pods
kubectl logs -n vacanceai deploy/backend -f          # Logs backend
kubectl logs -n vacanceai deploy/frontend -f         # Logs frontend

# Rebuild + redemarrer
docker build -t vacanceai-backend ./backend
kubectl rollout restart deploy/backend -n vacanceai

docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
kubectl rollout restart deploy/frontend -n vacanceai

# Sante
curl http://localhost/api/health
curl http://localhost/api/ready

# Tout supprimer
kubectl delete -f k8s/
```

---

## Developpement local (sans Docker/K8s)

### Backend

```bash
cd backend
python -m venv venv
.\venv\Scripts\activate   # Windows
pip install -r requirements.txt

# Oracle doit tourner sur localhost:1521
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

Le backend dispose d'un systeme de logging centralise qui ecrit dans `backend/log_apps/`.

| Fichier | Contenu | Niveau |
|---------|---------|--------|
| `app.log` | Logs generaux de l'application | INFO+ |
| `agents.log` | Activite des agents IA (orchestrateur, UI, database) | DEBUG+ |
| `sql.log` | Toutes les requetes SQL | DEBUG+ |
| `errors.log` | Erreurs de tous les loggers | ERROR+ |

- **Configuration** : `backend/logging_config.py` (`setup_logging()` appele au startup FastAPI)
- **Rotation** : 5 MB max par fichier, 3 backups
- **Volume K8s** : hostPath monte depuis le pod `/app/log_apps` vers `backend/log_apps/` local

```bash
cat backend/log_apps/app.log      # Logs generaux
cat backend/log_apps/sql.log      # Requetes SQL
cat backend/log_apps/agents.log   # Agents IA
cat backend/log_apps/errors.log   # Erreurs
```

---

## Troubleshooting

### Backend ne demarre pas (readiness 503)

Le readiness probe verifie la connexion Oracle. Verifier qu'Oracle tourne :

```bash
docker compose ps   # oracle-xe doit etre "healthy"
```

### ErrImageNeverPull dans K8s

Les images Docker n'existent pas localement. Builder d'abord :

```bash
docker build -t vacanceai-backend ./backend
docker build -t vacanceai-frontend -f frontend/Dockerfile.prod ./frontend
kubectl rollout restart deploy/backend deploy/frontend -n vacanceai
```

### Reset complet

```bash
kubectl delete -f k8s/
docker compose down
docker volume create oracle-xe-data
docker compose up -d
# Attendre healthy, puis re-seed et re-deployer
```
