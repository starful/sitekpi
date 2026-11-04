#!/bin/bash
# SiteKPI launchd helper: on | off | status | log
set -euo pipefail
LABEL=com.starful.sitekpi
ROOT="$(cd "$(dirname "$0")" && pwd)"
SRC="$ROOT/mac/${LABEL}.plist"
PLIST="$HOME/Library/LaunchAgents/${LABEL}.plist"
UID_N="$(id -u)"
DOMAIN="gui/${UID_N}"
PORT=8766

install_plist() {
  mkdir -p "$HOME/Library/LaunchAgents" "$ROOT/.data/logs"
  cp "$SRC" "$PLIST"
}

case "${1:-status}" in
  on|start|load)
    install_plist
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    launchctl bootstrap "$DOMAIN" "$PLIST"
    launchctl enable "$DOMAIN/$LABEL" 2>/dev/null || true
    launchctl kickstart -k "$DOMAIN/$LABEL"
    echo "SiteKPI on → http://127.0.0.1:${PORT}"
    ;;
  off|stop|unload)
    launchctl bootout "$DOMAIN/$LABEL" 2>/dev/null || true
    pids="$(lsof -nP -iTCP:${PORT} -sTCP:LISTEN -t 2>/dev/null || true)"
    if [ -n "${pids}" ]; then kill ${pids} 2>/dev/null || true; fi
    echo "SiteKPI off"
    ;;
  status)
    if launchctl print "$DOMAIN/$LABEL" >/dev/null 2>&1; then
      echo "loaded: $LABEL"
    else
      echo "not loaded"
    fi
    lsof -nP -iTCP:${PORT} -sTCP:LISTEN 2>/dev/null | head -3 || echo "${PORT}: not listening"
    ;;
  log|logs)
    tail -n "${2:-40}" "$ROOT/.data/logs/launchd-stdout.log" "$ROOT/.data/logs/launchd-stderr.log" 2>/dev/null || true
    ;;
  *)
    echo "usage: $0 on|off|status|log" >&2
    exit 2
    ;;
esac
