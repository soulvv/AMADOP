$dashboardJson = @"
{
  "title": "AMADOP Platform Overview",
  "uid": "amadop-overview",
  "version": 2,
  "schemaVersion": 36,
  "refresh": "10s",
  "time": { "from": "now-1h", "to": "now" },
  "panels": [
    {
      "id": 9,
      "title": "Total Registered Users",
      "type": "stat",
      "gridPos": { "x": 0, "y": 0, "w": 6, "h": 5 },
      "datasource": "PostgreSQL",
      "targets": [
        {
          "format": "table",
          "rawSql": "SELECT count(id) FROM users",
          "refId": "A"
        }
      ]
    },
    {
      "id": 10,
      "title": "Total Posts",
      "type": "stat",
      "gridPos": { "x": 6, "y": 0, "w": 6, "h": 5 },
      "datasource": "PostgreSQL",
      "targets": [
        {
          "format": "table",
          "rawSql": "SELECT count(id) FROM posts",
          "refId": "A"
        }
      ]
    },
    {
      "id": 11,
      "title": "Total Comments",
      "type": "stat",
      "gridPos": { "x": 12, "y": 0, "w": 6, "h": 5 },
      "datasource": "PostgreSQL",
      "targets": [
        {
          "format": "table",
          "rawSql": "SELECT count(id) FROM comments",
          "refId": "A"
        }
      ]
    },
    {
      "id": 12,
      "title": "Active Users (Last 24h)",
      "type": "stat",
      "gridPos": { "x": 18, "y": 0, "w": 6, "h": 5 },
      "datasource": "PostgreSQL",
      "targets": [
        {
          "format": "table",
          "rawSql": "SELECT count(id) FROM users WHERE last_login > NOW() - INTERVAL '24 hours'",
          "refId": "A"
        }
      ]
    },
    {
      "id": 13,
      "title": "User Activity Log",
      "type": "table",
      "gridPos": { "x": 0, "y": 5, "w": 24, "h": 7 },
      "datasource": "PostgreSQL",
      "targets": [
        {
          "format": "table",
          "rawSql": "SELECT username, last_login, last_logout FROM users ORDER BY last_login DESC NULLS LAST LIMIT 100",
          "refId": "A"
        }
      ]
    },
    {
      "id": 5,
      "title": "Pod Restart Count",
      "type": "stat",
      "gridPos": { "x": 0, "y": 12, "w": 12, "h": 6 },
      "targets": [
        {
          "expr": "sum(kube_pod_container_status_restarts_total{namespace=\"amadop\"}) by (pod)",
          "legendFormat": "{{pod}}"
        }
      ]
    },
    {
      "id": 6,
      "title": "Request Latency (p95)",
      "type": "timeseries",
      "gridPos": { "x": 12, "y": 12, "w": 12, "h": 6 },
      "targets": [
        {
          "expr": "histogram_quantile(0.95, sum(rate(http_request_duration_seconds_bucket[5m])) by (le, app))",
          "legendFormat": "{{app}} p95"
        }
      ]
    },
    {
      "id": 7,
      "title": "HPA Replica Count",
      "type": "stat",
      "gridPos": { "x": 0, "y": 18, "w": 12, "h": 5 },
      "targets": [
        {
          "expr": "kube_horizontalpodautoscaler_status_current_replicas{namespace=\"amadop\"}",
          "legendFormat": "{{horizontalpodautoscaler}}"
        }
      ]
    },
    {
      "id": 8,
      "title": "Running Pods in amadop namespace",
      "type": "stat",
      "gridPos": { "x": 12, "y": 18, "w": 12, "h": 5 },
      "targets": [
        {
          "expr": "count(kube_pod_status_phase{namespace=\"amadop\", phase=\"Running\"})",
          "legendFormat": "Running Pods"
        }
      ]
    }
  ]
}
"@

$payload = @{
    dashboard = $dashboardJson | ConvertFrom-Json
    overwrite = $true
} | ConvertTo-Json -Depth 10

$pair = "admin:jnR4EasKMK6BSnW3x1hgGgZ4af5dMjIDSx76mkeo"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)
$basicAuthValue = "Basic $base64"

$headers = @{
    Authorization = $basicAuthValue
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:3000/api/dashboards/db" -Method Post -Headers $headers -Body $payload
