#!/bin/bash
# One-time Google Cloud setup for SiteKPI. Safe to run again (each step skips what exists).
#
#   scripts/gcp_setup.sh ./client_secret_XXXX.json      # secrets, IAM, APIs, TTL
#   scripts/gcp_setup.sh --domain                        # after the first deploy: map sitekpi.net
#
# Runs with YOUR gcloud login. The OAuth client file is read locally and sent only to
# Secret Manager; nothing is printed. Delete the JSON file afterwards (or keep it out of git).
set -euo pipefail

PROJECT="${GCP_PROJECT_ID:-starful-258005}"     # Cloud Run, Firestore, Secret Manager
OAUTH_PROJECT="${OAUTH_PROJECT_ID:-sitekpi}"     # OAuth consent screen + client
REGION="${REGION:-us-central1}"
SERVICE="${SERVICE:-sitekpi-service}"
DOMAIN="${SITE_DOMAIN:-sitekpi.net}"

step() { echo ""; echo "▶ $1"; }

if [ "${1:-}" = "--domain" ]; then
  step "Domain mapping: ${DOMAIN} → ${SERVICE} (${REGION})"
  echo "  先に Search Console で ${DOMAIN} の所有権を確認しておく必要があります（この gcloud アカウントで）。"
  gcloud beta run domain-mappings create --service "$SERVICE" --domain "$DOMAIN" \
    --region "$REGION" --project "$PROJECT" || true
  step "DNS に登録するレコード"
  gcloud beta run domain-mappings describe --domain "$DOMAIN" --region "$REGION" --project "$PROJECT" \
    --format="table(status.resourceRecords[].type, status.resourceRecords[].name, status.resourceRecords[].rrdata)"
  exit 0
fi

CLIENT_JSON="${1:-}"
[ -f "$CLIENT_JSON" ] || { echo "使い方: scripts/gcp_setup.sh ./client_secret_XXXX.json"; exit 1; }

step "APIs (${PROJECT})"
gcloud services enable run.googleapis.com cloudbuild.googleapis.com artifactregistry.googleapis.com \
  secretmanager.googleapis.com firestore.googleapis.com --project "$PROJECT"

step "APIs for the OAuth client (${OAUTH_PROJECT}): Analytics Admin / Data"
gcloud services enable analyticsadmin.googleapis.com analyticsdata.googleapis.com --project "$OAUTH_PROJECT"

step "Artifact Registry repo: sitekpi (${REGION})"
gcloud artifacts repositories describe sitekpi --location "$REGION" --project "$PROJECT" >/dev/null 2>&1 \
  || gcloud artifacts repositories create sitekpi --repository-format=docker --location "$REGION" --project "$PROJECT"

put_secret() {  # name, value from stdin
  local name="$1"
  if gcloud secrets describe "$name" --project "$PROJECT" >/dev/null 2>&1; then
    gcloud secrets versions add "$name" --data-file=- --project "$PROJECT" >/dev/null
  else
    gcloud secrets create "$name" --data-file=- --replication-policy=automatic --project "$PROJECT" >/dev/null
  fi
  echo "  ✓ $name"
}

step "Secrets (values are not shown)"
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); w=d.get("web") or d[next(iter(d))]; sys.stdout.write(w["client_id"])' "$CLIENT_JSON" | put_secret SITEKPI_GOOGLE_CLIENT_ID
python3 -c 'import json,sys; d=json.load(open(sys.argv[1])); w=d.get("web") or d[next(iter(d))]; sys.stdout.write(w["client_secret"])' "$CLIENT_JSON" | put_secret SITEKPI_GOOGLE_CLIENT_SECRET
if gcloud secrets describe SITEKPI_SESSION_SECRET --project "$PROJECT" >/dev/null 2>&1; then
  echo "  ✓ SITEKPI_SESSION_SECRET (kept — changing it signs everyone out)"
else
  python3 -c 'import secrets,sys; sys.stdout.write(secrets.token_urlsafe(48))' | put_secret SITEKPI_SESSION_SECRET
fi

step "Runtime service account: read the secrets, use Firestore"
NUM="$(gcloud projects describe "$PROJECT" --format='value(projectNumber)')"
SA="${NUM}-compute@developer.gserviceaccount.com"
for s in SITEKPI_GOOGLE_CLIENT_ID SITEKPI_GOOGLE_CLIENT_SECRET SITEKPI_SESSION_SECRET; do
  gcloud secrets add-iam-policy-binding "$s" --member "serviceAccount:${SA}" \
    --role roles/secretmanager.secretAccessor --project "$PROJECT" >/dev/null
done
gcloud projects add-iam-policy-binding "$PROJECT" --member "serviceAccount:${SA}" \
  --role roles/datastore.user --condition=None >/dev/null
echo "  ✓ ${SA}"

step "Firestore TTL: old sessions are deleted automatically (field expire_at)"
gcloud firestore fields ttls update expire_at --collection-group=rows --enable-ttl \
  --project "$PROJECT" --async >/dev/null 2>&1 && echo "  ✓ requested" || echo "  (skip: run it later from the console)"

echo ""
echo "✅ 完了。次: ./deploy.sh → scripts/gcp_setup.sh --domain"
