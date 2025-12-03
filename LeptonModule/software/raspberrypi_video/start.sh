#!/bin/bash
# =====================================================
# start.sh — Démarrage du backend FLIR Lepton (lepton_capture)
# =====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEPTON_BIN="$SCRIPT_DIR/software/raspberrypi_video/lepton_capture"
PID_FILE="/tmp/lepton_capture.pid"
LOG_FILE="/tmp/lepton_capture.log"

if [ ! -x "$LEPTON_BIN" ]; then
  echo "❌ Binaire introuvable ou non exécutable : $LEPTON_BIN"
  echo "   -> Lance d'abord ./setup.sh puis ./init.sh."
  exit 1
fi

# Si un ancien process tourne encore, on le stoppe
if [ -f "$PID_FILE" ]; then
  OLD_PID=$(cat "$PID_FILE")
  if ps -p "$OLD_PID" > /dev/null 2>&1; then
    echo "🛑 Arrêt de l'ancien processus lepton_capture (PID: $OLD_PID)..."
    kill "$OLD_PID" 2>/dev/null || true
    sleep 1
  fi
  rm -f "$PID_FILE"
fi

echo "🚀 Démarrage de lepton_capture..."
"$LEPTON_BIN" > "$LOG_FILE" 2>&1 &
NEW_PID=$!

echo "$NEW_PID" > "$PID_FILE"
echo "✅ lepton_capture lancé (PID: $NEW_PID)"
echo "📝 Logs : $LOG_FILE"
