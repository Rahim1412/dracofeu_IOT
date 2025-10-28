#!/bin/bash
# =====================================================
# start.sh — Démarrage du flux FLIR Lepton
# =====================================================

set -e

# Aller dans le dossier du binaire
cd "$(dirname "$0")/software/v4l2lepton" || {
  echo "❌ Dossier software/v4l2lepton introuvable."
  exit 1
}

# Charger le module v4l2loopback si non présent
if ! lsmod | grep -q v4l2loopback; then
  echo "🎥 Chargement du module v4l2loopback..."
  sudo modprobe v4l2loopback video_nr=1 exclusive_caps=0
fi

# Lancer v4l2lepton en arrière-plan
echo "🚀 Démarrage du flux vidéo..."
sudo ./v4l2lepton -v /dev/video1 -d /dev/spidev0.0 > /tmp/lepton.log 2>&1 &

# Sauvegarde du PID pour stop.sh
echo $! > /tmp/lepton.pid
echo "✅ Flux vidéo lancé (PID: $(cat /tmp/lepton.pid))"
