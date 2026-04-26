#!/bin/bash
set -e

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
  echo "ERROR: kubectl not found on PATH. Please install kubectl first."
  exit 1
fi

echo "=== AMADOP Kubernetes Deployment ==="
echo ""

# Step 1: Point Docker to Minikube's daemon (build images inside Minikube)
echo "[0/11] Configuring Docker to use Minikube's daemon..."
eval $(minikube docker-env)

# Step 2: Build Docker images inside Minikube
echo "[1/11] Building Docker images inside Minikube..."
docker build -t amadop-auth_service:latest ./backend/auth_service
docker build -t amadop-post_service:latest ./backend/post_service
docker build -t amadop-comment_service:latest ./backend/comment_service
docker build -t amadop-notification_service:latest ./backend/notification_service
docker build -t amadop-ai_service:latest ./backend/ai_service
docker build -t amadop-frontend:latest ./frontend

echo "[2/11] Creating namespace..."
kubectl apply -f k8s/namespace.yaml

echo "[3/11] Applying secrets and configmap..."
kubectl apply -f k8s/secrets.yaml
kubectl apply -f k8s/configmap.yaml

echo "[4/11] Deploying PostgreSQL..."
kubectl apply -f k8s/postgres-pvc.yaml
kubectl apply -f k8s/postgres-deployment.yaml
kubectl apply -f k8s/postgres-service.yaml

echo "Waiting for PostgreSQL to be ready..."
kubectl rollout status deployment/postgres -n amadop --timeout=120s

echo "[5/11] Deploying Auth Service..."
kubectl apply -f k8s/auth-deployment.yaml
kubectl apply -f k8s/auth-service.yaml

echo "[6/11] Deploying Post Service..."
kubectl apply -f k8s/post-deployment.yaml
kubectl apply -f k8s/post-service.yaml

echo "[7/11] Deploying Comment Service..."
kubectl apply -f k8s/comment-deployment.yaml
kubectl apply -f k8s/comment-service.yaml

echo "[8/11] Deploying Notification Service..."
kubectl apply -f k8s/notification-deployment.yaml
kubectl apply -f k8s/notification-service.yaml

echo "[8.5/11] Deploying AI Service..."
kubectl apply -f k8s/ai-deployment.yaml
kubectl apply -f k8s/ai-service.yaml

echo "[9/11] Deploying Frontend..."
kubectl apply -f k8s/frontend-deployment.yaml
kubectl apply -f k8s/frontend-service.yaml

echo "[10/11] Applying Horizontal Pod Autoscalers..."
kubectl apply -f k8s/post-hpa.yaml
kubectl apply -f k8s/comment-hpa.yaml

echo "[11/11] Waiting for all deployments to be ready..."
kubectl rollout status deployment/auth-deployment -n amadop --timeout=120s
kubectl rollout status deployment/post-deployment -n amadop --timeout=120s
kubectl rollout status deployment/comment-deployment -n amadop --timeout=120s
kubectl rollout status deployment/notification-deployment -n amadop --timeout=120s
kubectl rollout status deployment/ai-deployment -n amadop --timeout=120s
kubectl rollout status deployment/frontend-deployment -n amadop --timeout=120s

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "All pods:"
kubectl get pods -n amadop
echo ""
echo "All services:"
kubectl get svc -n amadop
echo ""
echo "HPAs:"
kubectl get hpa -n amadop
echo ""
echo "Frontend URL:"
minikube service frontend-service -n amadop --url
