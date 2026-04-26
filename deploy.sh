#!/bin/bash
set -e
PROJECT_ID="nexus-social-494413"          # ← SET YOUR GCP PROJECT ID
REGION="us-central1"
SERVICE_NAME="nexus-social-py"
IMAGE="gcr.io/${PROJECT_ID}/${SERVICE_NAME}"
SA="nexus-sa"
SECRET="gemini-api-key"

GREEN='\033[0;32m'; BLUE='\033[0;34m'; NC='\033[0m'
log(){ echo -e "${BLUE}[Nexus]${NC} $1"; }
ok(){ echo -e "${GREEN}[✓]${NC} $1"; }

[ -z "$PROJECT_ID" ] && echo "Set PROJECT_ID in deploy.sh" && exit 1

gcloud config set project "${PROJECT_ID}"
gcloud services enable run.googleapis.com containerregistry.googleapis.com \
  cloudbuild.googleapis.com secretmanager.googleapis.com --quiet
ok "APIs enabled"

SA_EMAIL="${SA}@${PROJECT_ID}.iam.gserviceaccount.com"
gcloud iam service-accounts describe "${SA_EMAIL}" &>/dev/null || \
  gcloud iam service-accounts create "${SA}" --display-name="Nexus App SA"
gcloud projects add-iam-policy-binding "${PROJECT_ID}" \
  --member="serviceAccount:${SA_EMAIL}" --role="roles/secretmanager.secretAccessor" --quiet
ok "Service account ready"

if ! gcloud secrets describe "${SECRET}" --project="${PROJECT_ID}" &>/dev/null; then
  read -sp "Enter Gemini API key: " KEY; echo
  echo -n "${KEY}" | gcloud secrets create "${SECRET}" --data-file=- --replication-policy=automatic
  ok "Secret stored"
fi

log "Building Docker image..."
gcloud builds submit --tag "${IMAGE}:latest" --timeout=15m .
ok "Image built"

log "Deploying to Cloud Run ${REGION}..."
gcloud run deploy "${SERVICE_NAME}" \
  --image="${IMAGE}:latest" --platform=managed --region="${REGION}" \
  --service-account="${SA_EMAIL}" --allow-unauthenticated \
  --port=8080 --memory=1Gi --cpu=1 \
  --min-instances=0 --max-instances=10 --timeout=60 \
  --set-env-vars="ENVIRONMENT=production,SECRET_NAME=${SECRET},GCP_PROJECT_ID=${PROJECT_ID}" \
  --set-secrets="GEMINI_API_KEY=${SECRET}:latest" --quiet

URL=$(gcloud run services describe "${SERVICE_NAME}" \
  --platform=managed --region="${REGION}" --format="value(status.url)")

echo -e "\n${GREEN}Nexus Social (Python) is LIVE! 🚀${NC}"
echo -e "App:      ${BLUE}${URL}${NC}"
echo -e "API docs: ${BLUE}${URL}/api/docs${NC}"
echo -e "Health:   ${BLUE}${URL}/health${NC}"
