#!/bin/bash
# SiteKPI → Cloud Run via Cloud Build (cloudbuild.yaml). Same flow as jpcampus.
#   ./deploy.sh            tests on Cloud Build, build, push, deploy
#   ./deploy.sh --check    run the tests locally only
# One-time setup first: scripts/gcp_setup.sh
set -euo pipefail
cd "$(dirname "$0")"

GCP_PROJECT_ID="${GCP_PROJECT_ID:-starful-258005}"
SITE_DOMAIN="${SITE_DOMAIN:-sitekpi.net}"
# Optional, shown in /policy and /terms: OPERATOR_NAME, OPERATOR_ADDRESS, LEGAL_COURT
OPERATOR_NAME="${OPERATOR_NAME:-}"
OPERATOR_ADDRESS="${OPERATOR_ADDRESS:-}"
LEGAL_COURT="${LEGAL_COURT:-}"

if [ "${1:-}" = "--check" ]; then
  PY="${PY:-.venv/bin/python}"; [ -x "$PY" ] || PY=python3
  "$PY" -m pytest -q
  exit 0
fi

command -v gcloud >/dev/null 2>&1 || { echo "gcloud がありません"; exit 1; }
if [ -n "$(git status --porcelain -- sitekpi static main.py requirements.txt 2>/dev/null)" ]; then
  echo "⚠️  コミットしていない変更があります（そのままアップロードされます）"
fi
echo "▶ SiteKPI → https://${SITE_DOMAIN}  (project: ${GCP_PROJECT_ID})"
gcloud builds submit --config=cloudbuild.yaml --project "$GCP_PROJECT_ID" \
  --substitutions="^@^_DOMAIN=${SITE_DOMAIN}@_OPERATOR_NAME=${OPERATOR_NAME}@_OPERATOR_ADDRESS=${OPERATOR_ADDRESS}@_LEGAL_COURT=${LEGAL_COURT}"
echo "✅ deployed → https://${SITE_DOMAIN}"
