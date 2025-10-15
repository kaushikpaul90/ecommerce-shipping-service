#!/bin/bash
set -e

echo "🚀 Starting deployment of Shipping microservice to Minikube..."

# Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
  echo "🔧 Starting Minikube..."
  minikube start
else
  echo "✅ Minikube already running."
fi

echo "📦 Applying Kubernetes manifests..."

# Apply all manifests
kubectl apply -f k8s/shipping-deployment-template.yaml
kubectl apply -f k8s/shipping-service-template.yaml

echo "⏳ Waiting for all pods to become ready..."
kubectl wait --for=condition=available --timeout=120s deployment/shipping-service

echo "✅ Shipping service deployed successfully!"

echo ""
echo "🌐 Access Shipping service via the following URL:"

# Retrieve and print service URL
echo "Shipping service: $(minikube service shipping-service --url)"

echo ""
echo "🎉 Deployment complete!"
