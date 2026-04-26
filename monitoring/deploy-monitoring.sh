#!/bin/bash
set -e

# Check for helm
if ! command -v helm &> /dev/null; then
  echo "ERROR: helm not found on PATH. Install Helm v3 first: https://helm.sh/docs/intro/install/"
  exit 1
fi

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
  echo "ERROR: kubectl not found on PATH."
  exit 1
fi

echo "=== AMADOP Monitoring Stack Deployment ==="
echo ""

# Step 1: Create monitoring namespace
echo "[1/6] Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Add Helm repos
echo "[2/6] Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Step 3: Install kube-prometheus-stack (Prometheus + kube-state-metrics + node-exporter)
echo "[3/6] Installing kube-prometheus-stack..."
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack \
  --namespace monitoring \
  --values monitoring/prometheus-values.yaml \
  --wait \
  --timeout 5m

# Step 4: Install Grafana
echo "[4/6] Installing Grafana..."
helm upgrade --install grafana grafana/grafana \
  --namespace monitoring \
  --values monitoring/grafana-values.yaml \
  --wait \
  --timeout 3m

# Step 5: Apply Grafana dashboard ConfigMap
echo "[5/6] Loading AMADOP dashboard into Grafana..."
kubectl apply -f monitoring/grafana-dashboard-configmap.yaml

# Step 6: Print access info
echo ""
echo "[6/6] Getting access URLs..."
echo ""
echo "=== Monitoring Stack Ready! ==="
echo ""
echo "Grafana URL:"
minikube service grafana -n monitoring --url 2>/dev/null || \
  echo "  Run: kubectl port-forward svc/grafana 3000:80 -n monitoring"
echo ""
echo "Grafana credentials:"
echo "  Username: admin"
echo "  Password: amadop-admin"
echo ""
echo "Prometheus URL:"
minikube service kube-prometheus-stack-prometheus -n monitoring --url 2>/dev/null || \
  echo "  Run: kubectl port-forward svc/kube-prometheus-stack-prometheus 9090:9090 -n monitoring"
echo ""
echo "Verify Prometheus targets:"
echo "  Open Prometheus UI → Status → Targets"
echo "  You should see amadop-services targets listed"
