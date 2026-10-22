#!/usr/bin/env bash
# SiteKPI local dev server.
#   ./run.sh            → http://127.0.0.1:8766
#   PORT=9000 ./run.sh  → change port
# Recreates .venv if it is missing/broken (e.g. after the folder was renamed)
# and reinstalls packages when requirements.txt changes.
set -euo pipefail

cd "$(dirname "$0")"
PORT="${PORT:-8766}"
HOST="127.0.0.1"   # keep 127.0.0.1 — matches GOOGLE_REDIRECT_URI
VENV=".venv"
STAMP="$VENV/.requirements.sha"

pick_python() {
  for c in python3.14 python3.13 python3.12 python3; do
    if command -v "$c" >/dev/null 2>&1 &&
       "$c" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null; then
      echo "$c"; return 0
    fi
  done
  return 1
}

venv_ok() {
  [ -x "$VENV/bin/python" ] &&
  "$VENV/bin/python" -c 'import sys; sys.exit(0 if sys.version_info >= (3, 12) else 1)' 2>/dev/null
}

if ! venv_ok; then
  PY="$(pick_python)" || {
    echo "✗ Python 3.12 以上が見つかりません。brew install python@3.14 などで入れてください。" >&2
    exit 1
  }
  echo "→ .venv を作り直します（$($PY --version)）"
  rm -rf "$VENV"
  "$PY" -m venv "$VENV"
  rm -f "$STAMP"
fi

REQ_SHA="$(shasum requirements.txt | awk '{print $1}')"
if [ ! -f "$STAMP" ] || [ "$(cat "$STAMP")" != "$REQ_SHA" ]; then
  echo "→ パッケージをインストールします"
  "$VENV/bin/python" -m pip install -q --upgrade pip
  "$VENV/bin/python" -m pip install -q -r requirements.txt
  echo "$REQ_SHA" > "$STAMP"
fi

if [ ! -f .env ]; then
  echo "! .env がありません。cp .env.example .env して値を入れてください（デモ接続はそのままでも動きます）。"
fi

URL="http://$HOST:$PORT"
echo "✓ SiteKPI → $URL   （止めるときは Ctrl+C）"
( sleep 2; command -v open >/dev/null 2>&1 && open "$URL/connect" ) >/dev/null 2>&1 &
exec "$VENV/bin/python" -m uvicorn main:app --host "$HOST" --port "$PORT" --reload
