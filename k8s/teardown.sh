#!/bin/bash

# Check for kubectl
if ! command -v kubectl &> /dev/null; then
  echo "ERROR: kubectl not found on PATH."
  exit 1
fi

echo "=== Tearing down AMADOP from Kubernetes ==="
echo "This will delete the 'amadop' namespace and ALL resources within it."
read -p "Are you sure? (yes/no): " confirm

if [ "$confirm" != "yes" ]; then
  echo "Aborted."
  exit 0
fi

kubectl delete namespace amadop --ignore-not-found=true

echo ""
echo "=== Teardown Complete ==="
echo "The 'amadop' namespace and all its resources have been deleted."
