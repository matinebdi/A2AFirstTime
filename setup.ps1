# ============================================
# VacanceAI - Setup Automatique
# Deploie Oracle + Build Images + Kubernetes
# Usage: .\setup.ps1
# ============================================

param(
    [switch]$SkipOracle,
    [switch]$SkipBuild,
    [switch]$SkipSchema
)

$ErrorActionPreference = "Stop"
$ProjectRoot = $PSScriptRoot

# --------------------------------------------
# Couleurs et affichage
# --------------------------------------------
function Write-Step($msg)  { Write-Host "`n>> $msg" -ForegroundColor Cyan }
function Write-Ok($msg)    { Write-Host "   [OK] $msg" -ForegroundColor Green }
function Write-Warn($msg)  { Write-Host "   [!] $msg" -ForegroundColor Yellow }
function Write-Fail($msg)  { Write-Host "   [ERREUR] $msg" -ForegroundColor Red }

Write-Host ""
Write-Host "========================================" -ForegroundColor Magenta
Write-Host "  VacanceAI - Setup Automatique" -ForegroundColor Magenta
Write-Host "========================================" -ForegroundColor Magenta

# ============================================
# ETAPE 1 : Verification des prerequis
# ============================================
Write-Step "Verification des prerequis..."

# Docker
if (-not (Get-Command docker -ErrorAction SilentlyContinue)) {
    Write-Fail "Docker non trouve. Installez Docker Desktop."
    exit 1
}
docker info *>$null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Docker Desktop n'est pas demarre. Lancez-le et reessayez."
    exit 1
}
Write-Ok "Docker Desktop actif"

# kubectl
if (-not (Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Fail "kubectl non trouve. Activez Kubernetes dans Docker Desktop > Settings > Kubernetes."
    exit 1
}
Write-Ok "kubectl disponible"

# Kubernetes cluster
kubectl cluster-info *>$null
if ($LASTEXITCODE -ne 0) {
    Write-Fail "Cluster Kubernetes non accessible. Activez-le dans Docker Desktop > Settings > Kubernetes."
    exit 1
}
Write-Ok "Cluster Kubernetes actif"

# .env
$envFile = Join-Path $ProjectRoot ".env"
if (-not (Test-Path $envFile)) {
    Write-Fail "Fichier .env introuvable. Copiez .env.example en .env et remplissez les valeurs."
    exit 1
}
Write-Ok "Fichier .env present"

# ============================================
# ETAPE 2 : Demarrage Oracle (Docker Compose)
# ============================================
if (-not $SkipOracle) {
    Write-Step "Demarrage Oracle 21c XE..."

    docker compose -f "$ProjectRoot\compose.yaml" up -d
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec docker compose up. Verifiez que le volume 'oracle-xe-data' existe (docker volume create oracle-xe-data)."
        exit 1
    }
    Write-Ok "Conteneur Oracle lance"

    # Attente que Oracle soit pret
    Write-Step "Attente qu'Oracle soit pret (peut prendre 1-2 min)..."
    $maxRetries = 40
    $retry = 0
    $oracleReady = $false

    while ($retry -lt $maxRetries) {
        $retry++
        $health = docker inspect --format='{{.State.Health.Status}}' oracle-xe 2>$null
        if ($health -eq "healthy") {
            $oracleReady = $true
            break
        }

        # Fallback: tester directement la connexion
        $testResult = docker exec oracle-xe sh -c "echo 'SELECT 1 FROM DUAL;' | sqlplus -s SYS/admin@//localhost:1521/XE as SYSDBA" 2>$null
        if ($testResult -match "1") {
            $oracleReady = $true
            break
        }

        Write-Host "   [$retry/$maxRetries] Oracle demarre..." -ForegroundColor DarkGray
        Start-Sleep -Seconds 5
    }

    if (-not $oracleReady) {
        Write-Fail "Oracle n'a pas demarre dans le temps imparti. Verifiez: docker logs oracle-xe"
        exit 1
    }
    Write-Ok "Oracle est pret"
} else {
    Write-Warn "Oracle ignore (-SkipOracle)"
}

# ============================================
# ETAPE 3 : Initialisation du schema Oracle
# ============================================
if (-not $SkipSchema) {
    Write-Step "Initialisation du schema Oracle..."

    $schemaFile = Join-Path $ProjectRoot "backend\database\oracle_schema.sql"
    if (-not (Test-Path $schemaFile)) {
        Write-Fail "oracle_schema.sql introuvable dans backend/database/"
        exit 1
    }

    # Copier le schema dans le conteneur
    docker cp $schemaFile oracle-xe:/tmp/oracle_schema.sql
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Impossible de copier le schema dans le conteneur"
        exit 1
    }

    # Executer le schema
    docker exec oracle-xe bash -c "sqlplus SYS/admin@//localhost:1521/XE as SYSDBA @/tmp/oracle_schema.sql"
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "Le schema a peut-etre rencontre des erreurs (normal si les tables existent deja)"
    } else {
        Write-Ok "Schema Oracle initialise"
    }
} else {
    Write-Warn "Schema ignore (-SkipSchema)"
}

# ============================================
# ETAPE 4 : Build des images Docker
# ============================================
if (-not $SkipBuild) {
    Write-Step "Build de l'image backend..."
    docker build -t vacanceai-backend "$ProjectRoot\backend"
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec du build backend"
        exit 1
    }
    Write-Ok "Image vacanceai-backend:latest"

    Write-Step "Build de l'image frontend..."
    docker build -t vacanceai-frontend -f "$ProjectRoot\frontend\Dockerfile.prod" "$ProjectRoot\frontend"
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec du build frontend"
        exit 1
    }
    Write-Ok "Image vacanceai-frontend:latest"

    Write-Step "Build de l'image LangGraph Studio..."
    docker build -t vacanceai-langgraph -f "$ProjectRoot\backend\Dockerfile.langgraph" "$ProjectRoot\backend"
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec du build langgraph"
        exit 1
    }
    Write-Ok "Image vacanceai-langgraph:latest"
} else {
    Write-Warn "Build ignore (-SkipBuild)"
}

# ============================================
# ETAPE 5 : Installation Ingress NGINX
# ============================================
Write-Step "Verification Ingress NGINX Controller..."

$ingressNs = kubectl get namespace ingress-nginx --ignore-not-found -o name 2>$null
if (-not $ingressNs) {
    Write-Host "   Installation d'Ingress NGINX Controller..." -ForegroundColor DarkGray
    kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/controller-v1.12.0/deploy/static/provider/cloud/deploy.yaml
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec de l'installation d'Ingress NGINX"
        exit 1
    }

    # Attente que le controller soit pret
    Write-Host "   Attente du controller Ingress NGINX..." -ForegroundColor DarkGray
    $ingressRetry = 0
    $ingressReady = $false
    while ($ingressRetry -lt 30) {
        $ingressRetry++
        $pods = kubectl get pods -n ingress-nginx -l app.kubernetes.io/component=controller --no-headers 2>$null
        if ($pods -match "Running") {
            $ingressReady = $true
            break
        }
        Start-Sleep -Seconds 5
    }
    if (-not $ingressReady) {
        Write-Warn "Ingress NGINX Controller pas encore Ready, le deploiement continue..."
    } else {
        Write-Ok "Ingress NGINX Controller installe et pret"
    }
} else {
    Write-Ok "Ingress NGINX Controller deja installe"
}

# ============================================
# ETAPE 6 : Generation des secrets K8s
# ============================================
Write-Step "Generation des secrets Kubernetes depuis .env..."

# Lire le .env
$envVars = @{}
Get-Content $envFile | ForEach-Object {
    $line = $_.Trim()
    if ($line -and -not $line.StartsWith("#")) {
        $parts = $line -split "=", 2
        if ($parts.Length -eq 2) {
            $envVars[$parts[0].Trim()] = $parts[1].Trim()
        }
    }
}

# Encoder en base64
function To-Base64($str) {
    return [Convert]::ToBase64String([System.Text.Encoding]::UTF8.GetBytes($str))
}

$oraclePwd = To-Base64 "admin"
$oraclePassword = if ($envVars["ORACLE_PASSWORD"]) { To-Base64 $envVars["ORACLE_PASSWORD"] } else { To-Base64 "vacanceai" }
$jwtSecret = if ($envVars["JWT_SECRET_KEY"]) { To-Base64 $envVars["JWT_SECRET_KEY"] } else { To-Base64 "change-this-to-a-random-secret-key" }
$googleApiKey = if ($envVars["GOOGLE_API_KEY"]) { To-Base64 $envVars["GOOGLE_API_KEY"] } else { Write-Fail "GOOGLE_API_KEY manquant dans .env"; exit 1 }
$langchainApiKey = if ($envVars["LANGCHAIN_API_KEY"]) { To-Base64 $envVars["LANGCHAIN_API_KEY"] } else { Write-Warn "LANGCHAIN_API_KEY manquant dans .env (LangSmith desactive)"; $null }

$secretsYaml = @"
# VacanceAI Kubernetes Secrets (auto-generated by setup.ps1)
# Values are base64-encoded from .env
apiVersion: v1
kind: Secret
metadata:
  name: vacanceai-secrets
  namespace: vacanceai
type: Opaque
data:
  ORACLE_PWD: $oraclePwd
  ORACLE_PASSWORD: $oraclePassword
  JWT_SECRET_KEY: $jwtSecret
  GOOGLE_API_KEY: $googleApiKey
"@

if ($langchainApiKey) {
    $secretsYaml += "`n  LANGCHAIN_API_KEY: $langchainApiKey"
}

$secretsPath = Join-Path $ProjectRoot "k8s\secrets.yaml"
$secretsYaml | Out-File -FilePath $secretsPath -Encoding UTF8 -NoNewline
Write-Ok "k8s/secrets.yaml genere"

# ============================================
# ETAPE 7 : Deploiement Kubernetes
# ============================================
Write-Step "Deploiement des manifests Kubernetes..."

# Appliquer dans l'ordre
$manifests = @(
    "namespace.yaml",
    "configmap.yaml",
    "secrets.yaml",
    "jaeger.yaml",
    "backend.yaml",
    "frontend.yaml",
    "langgraph-studio.yaml",
    "ingress.yaml"
)

foreach ($manifest in $manifests) {
    $path = Join-Path $ProjectRoot "k8s\$manifest"
    kubectl apply -f $path
    if ($LASTEXITCODE -ne 0) {
        Write-Fail "Echec: kubectl apply -f k8s/$manifest"
        exit 1
    }
    Write-Ok $manifest
}

# ============================================
# ETAPE 8 : Attente des pods
# ============================================
Write-Step "Attente que les pods soient Ready..."

$deployments = @("backend", "frontend", "jaeger", "langgraph-studio")
foreach ($deploy in $deployments) {
    Write-Host "   Attente de $deploy..." -ForegroundColor DarkGray
    kubectl rollout status deployment/$deploy -n vacanceai --timeout=120s
    if ($LASTEXITCODE -ne 0) {
        Write-Warn "$deploy n'est pas pret. Verifiez: kubectl logs -n vacanceai deploy/$deploy"
    } else {
        Write-Ok "$deploy Ready"
    }
}

# ============================================
# RESULTAT FINAL
# ============================================
Write-Host ""
Write-Host "========================================" -ForegroundColor Green
Write-Host "  VacanceAI deploye avec succes !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Green
Write-Host ""
Write-Host "  URLs:" -ForegroundColor White
Write-Host "    Frontend :  http://localhost" -ForegroundColor Cyan
Write-Host "    API      :  http://localhost/api/health" -ForegroundColor Cyan
Write-Host "    Swagger  :  http://localhost/swagger" -ForegroundColor Cyan
Write-Host "    ReDoc    :  http://localhost/redoc" -ForegroundColor Cyan
Write-Host "    Jaeger   :  http://localhost:31686" -ForegroundColor Cyan
Write-Host "    LangGraph:  http://localhost:32024" -ForegroundColor Cyan
Write-Host "    Oracle   :  localhost:1521/XE" -ForegroundColor Cyan
Write-Host ""
Write-Host "  Commandes utiles:" -ForegroundColor White
Write-Host "    kubectl logs -n vacanceai deploy/backend -f" -ForegroundColor DarkGray
Write-Host "    kubectl logs -n vacanceai deploy/frontend -f" -ForegroundColor DarkGray
Write-Host "    .\teardown.ps1  (pour tout supprimer)" -ForegroundColor DarkGray
Write-Host ""
