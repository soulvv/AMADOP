$datasourceJson = @"
{
  "name": "PostgreSQL",
  "type": "postgres",
  "url": "postgres-service:5432",
  "access": "proxy",
  "user": "postgres",
  "database": "amadop_db",
  "secureJsonData": {
    "password": "postgres"
  },
  "jsonData": {
    "sslmode": "disable",
    "postgresVersion": 15
  }
}
"@

$pair = "admin:jnR4EasKMK6BSnW3x1hgGgZ4af5dMjIDSx76mkeo"
$bytes = [System.Text.Encoding]::ASCII.GetBytes($pair)
$base64 = [System.Convert]::ToBase64String($bytes)
$basicAuthValue = "Basic $base64"

$headers = @{
    Authorization = $basicAuthValue
    "Content-Type" = "application/json"
}

Invoke-RestMethod -Uri "http://localhost:3000/api/datasources" -Method Post -Headers $headers -Body $datasourceJson
