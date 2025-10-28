#!/bin/bash
# =====================================================
# stop.sh — Arrêt du flux FLIR Lepton
# =====================================================

# Vérifie si un PID est enregistré
if [ -f /tmp/lepton.pid ]; then
  PID=$(cat /tmp/lepton.pid)
  echo "🛑 Arrêt du flux vidéo (PID: $PID)..."
  sudo kill "$PID" 2>/dev/null || true
  rm /tmp/lepton.pid
  echo "✅ Flux arrêté."
else
  echo "⚠️ Aucun processus Lepton en cours (pas de /tmp/lepton.pid trouvé)."
fi
