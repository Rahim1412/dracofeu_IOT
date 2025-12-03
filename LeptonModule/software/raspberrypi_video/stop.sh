#!/bin/bash
# =====================================================
# stop.sh — Arrêt du backend FLIR Lepton (lepton_capture)
# =====================================================

PID_FILE="/tmp/lepton_capture.pid"

if [ -f "$PID_FILE" ]; then
  PID=$(cat "$PID_FILE")
  echo "🛑 Arrêt de lepton_capture (PID: $PID)..."
  kill "$PID" 2>/dev/null || true
  rm -f "$PID_FILE"
  echo "✅ Processus arrêté."
else
  echo "⚠️ Aucun PID enregistré dans $PID_FILE, tentative de kill par nom..."
  pkill lepton_capture 2>/dev/null || true
  echo "ℹ️ Si le backend ne tournait pas, c'est normal."
fi
