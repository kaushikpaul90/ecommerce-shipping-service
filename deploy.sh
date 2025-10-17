#!/bin/bash
set -e

echo "🚀 Starting deployment of Shipping microservice to Minikube..."

# --------------------------------------------------------------------
# 1. Load environment variables
# --------------------------------------------------------------------
# Load .env file if it exists
if [ -f .env ]; then
  echo "🔧 Loading environment variable(s) from .env"
  export $(grep -v '^#' .env | xargs)
else
  echo "⚠️ .env file not found! Make sure DOCKER_HUB_USERNAME is set."
  exit 1
fi

# Validate DOCKER_HUB_USERNAME
if [ -z "$DOCKER_HUB_USERNAME" ]; then
  echo "❌ DOCKER_HUB_USERNAME is not set. Exiting."
  exit 1
fi

# --------------------------------------------------------------------
# 2. Ensure Minikube is running
# --------------------------------------------------------------------
# Start Minikube if not running
if ! minikube status >/dev/null 2>&1; then
  echo "🔧 Starting Minikube..."
  minikube start
else
  echo "✅ Minikube already running."
fi

SERVICE_NAME="shipping-service"
CHART_DIR="helm_chart"

# --------------------------------------------------------------------
# 3. Remove any existing Kubernetes resources not managed by Helm
# --------------------------------------------------------------------
if kubectl get deployment "$SERVICE_NAME" >/dev/null 2>&1; then
  echo "🧹 Cleaning up old non-Helm deployment..."
  kubectl delete deployment "$SERVICE_NAME" --ignore-not-found
fi

if kubectl get service "$SERVICE_NAME" >/dev/null 2>&1; then
  kubectl delete service "$SERVICE_NAME" --ignore-not-found
fi

# --------------------------------------------------------------------
# 4. Resolve Helm values dynamically
# --------------------------------------------------------------------
# Resolve environment variables in values.yaml
echo "🔄 Generating Helm values file with environment variables..."
envsubst < "$CHART_DIR/values.yaml" > "$CHART_DIR/values-resolved.yaml"

# --------------------------------------------------------------------
# 5. Deploy using Helm
# --------------------------------------------------------------------
echo "📦 Deploying $SERVICE_NAME to Minikube via Helm..."
helm upgrade --install "$SERVICE_NAME" "$CHART_DIR" -f "$CHART_DIR/values-resolved.yaml"

# --------------------------------------------------------------------
# 6. Wait for pods to be ready
# --------------------------------------------------------------------
echo "⏳ Waiting for $SERVICE_NAME pods to become ready..."
kubectl rollout status deployment/$SERVICE_NAME --timeout=15s || {
  echo "⚠️ Deployment did not complete successfully. Check pod logs below:"
  kubectl get pods
  kubectl describe deployment $SERVICE_NAME
  exit 1
}

# --------------------------------------------------------------------
# 7. Display service URL
# --------------------------------------------------------------------
echo ""
echo "🌐 Access $SERVICE_NAME via the following URL:"
minikube service $SERVICE_NAME --url

# echo "📦 Applying Kubernetes manifests..."

# # Apply all manifests
# kubectl apply -f k8s/shipping-deployment-template.yaml
# kubectl apply -f k8s/shipping-service-template.yaml

# echo ${DOCKER_HUB_USERNAME}

# echo "⏳ Waiting for all pods to become ready..."
# kubectl wait --for=condition=available --timeout=15s deployment/shipping-service

# echo "✅ Shipping service deployed successfully!"

# echo ""
# echo "🌐 Access Shipping service via the following URL:"

# # Retrieve and print service URL
# echo "Shipping service: $(minikube service shipping-service --url)"

echo ""
echo "✅ $SERVICE_NAME deployed successfully!"
