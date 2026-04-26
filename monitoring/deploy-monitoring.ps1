# Check for helm
if (!(Get-Command helm -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: helm not found on PATH. Install Helm v3 first: https://helm.sh/docs/intro/install/"
    exit 1
}

# Check for kubectl
if (!(Get-Command kubectl -ErrorAction SilentlyContinue)) {
    Write-Error "ERROR: kubectl not found on PATH."
    exit 1
}

Write-Host "=== AMADOP Monitoring Stack Deployment ==="
Write-Host ""

# Step 1: Create monitoring namespace
Write-Host "[1/6] Creating monitoring namespace..."
kubectl create namespace monitoring --dry-run=client -o yaml | kubectl apply -f -

# Step 2: Add Helm repos
Write-Host "[2/6] Adding Helm repositories..."
helm repo add prometheus-community https://prometheus-community.github.io/helm-charts
helm repo add grafana https://grafana.github.io/helm-charts
helm repo update

# Step 3: Install kube-prometheus-stack
Write-Host "[3/6] Installing kube-prometheus-stack..."
helm upgrade --install kube-prometheus-stack prometheus-community/kube-prometheus-stack `
  --namespace monitoring `
  --values monitoring/prometheus-values.yaml `
  --wait `
  --timeout 5m

# Step 4: Install Grafana
Write-Host "[4/6] Installing Grafana..."
helm upgrade --install grafana grafana/grafana `
  --namespace monitoring `
  --values monitoring/grafana-values.yaml `
  --wait `
  --timeout 3m

# Step 5: Apply Grafana dashboard ConfigMap
Write-Host "[5/6] Loading AMADOP dashboard into Grafana..."
kubectl apply -f monitoring/grafana-dashboard-configmap.yaml

# Step 6: Print access info
Write-Host ""
Write-Host "[6/6] Getting access URLs..."
Write-Host ""
Write-Host "=== Monitoring Stack Ready! ==="
Write-Host ""
Write-Host "Grafana URL:"
& minikube service grafana -n monitoring --url
Write-Host ""
Write-Host "Grafana credentials:"
Write-Host "  Username: admin"
Write-Host "  Password: amadop-admin"
Write-Host ""
Write-Host "Prometheus URL:"
& minikube service kube-prometheus-stack-prometheus -n monitoring --url
Write-Host ""
Write-Host "Verify Prometheus targets:"
Write-Host "  Open Prometheus UI -> Status -> Targets"
Write-Host "  You should see amadop-services targets listed"
