# Check for kubectl
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: kubectl not found on PATH. Please install kubectl first."
    exit 1
}

Write-Host "=== AMADOP Kubernetes Deployment ==="
Write-Host ""

# Step 1: Point Docker to Minikube's daemon
Write-Host "[0/11] Configuring Docker to use Minikube's daemon..."
& minikube docker-env | Invoke-Expression

# Step 2: Build Docker images inside Minikube
Write-Host "[1/11] Building Docker images inside Minikube..."
docker build -t amadop-auth_service:latest ./backend/auth_service
docker build -t amadop-post_service:latest ./backend/post_service
docker build -t amadop-comment_service:latest ./backend/comment_service
docker build -t amadop-notification_service:latest ./backend/notification_service
docker build -t amadop-ai_service:latest ./backend/ai_service
docker build -t amadop-frontend:latest ./frontend

Write-Host "[2/11] Creating namespace..."
kubectl apply -f k8s/namespace.yaml

Write-Host "[3/11] Applying secrets and configmap..."
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

Write-Host "[4/11] Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

Write-Host "Waiting for PostgreSQL to be ready..."
kubectl rollout status deployment/postgres -n amadop --timeout=120s

Write-Host "[5/11] Deploying Auth Service..."
kubectl apply -f k8s/auth-deployment.yaml
kubectl apply -f k8s/auth-service.yaml

Write-Host "[6/11] Deploying Post Service..."
kubectl apply -f k8s/post-deployment.yaml
kubectl apply -f k8s/post-service.yaml

Write-Host "[7/11] Deploying Comment Service..."
kubectl apply -f k8s/comment-deployment.yaml
kubectl apply -f k8s/comment-service.yaml

Write-Host "[8/11] Deploying Notification Service..."
kubectl apply -f k8s/notification-deployment.yaml
kubectl apply -f k8s/notification-service.yaml

Write-Host "[8.5/11] Deploying AI Service..."
kubectl apply -f k8s/ai-deployment.yaml
kubectl apply -f k8s/ai-service.yaml

Write-Host "[9/11] Deploying Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

Write-Host "[10/11] Applying Horizontal Pod Autoscalers..."
kubectl apply -f k8s/post-hpa.yaml
kubectl apply -f k8s/comment-hpa.yaml

Write-Host "[11/11] Waiting for all deployments to be ready..."
kubectl rollout status deployment/auth-deployment -n amadop --timeout=120s
kubectl rollout status deployment/post-deployment -n amadop --timeout=120s
kubectl rollout status deployment/comment-deployment -n amadop --timeout=120s
kubectl rollout status deployment/notification-deployment -n amadop --timeout=120s
kubectl rollout status deployment/ai-deployment -n amadop --timeout=120s
kubectl rollout status deployment/frontend-deployment -n amadop --timeout=120s

Write-Host ""
Write-Host "=== Deployment Complete! ==="
Write-Host ""
Write-Host "All pods:"
kubectl get pods -n amadop
Write-Host ""
Write-Host "All services:"
kubectl get svc -n amadop
Write-Host ""
Write-Host "HPAs:"
kubectl get hpa -n amadop
Write-Host ""
Write-Host "Frontend URL:"
minikube service frontend-service -n amadop --url
