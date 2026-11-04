# SiteKPI on Cloud Run (see deploy.sh / cloudbuild.yaml). Local development uses run.sh instead.
FROM python:3.12-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PORT=8080

WORKDIR /code

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY main.py ./
COPY sitekpi ./sitekpi
COPY static ./static

# Cloud Run terminates TLS: trust its X-Forwarded-* headers so request URLs are https.
CMD exec uvicorn main:app --host 0.0.0.0 --port "${PORT}" --proxy-headers --forwarded-allow-ips="*"
