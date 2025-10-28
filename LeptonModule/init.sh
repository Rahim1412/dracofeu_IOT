#!/bin/bash
# =====================================================
# Script d’initialisation du module v4l2loopback
# pour la caméra FLIR Lepton
# =====================================================

set -e  # Stoppe le script si une commande échoue

echo "🔧 (1/2) Suppression de toute instance précédente du module v4l2loopback..."
sudo modprobe -r v4l2loopback 2>/dev/null || true

echo "🎥 (2/2) Chargement du module v4l2loopback..."
sudo modprobe v4l2loopback video_nr=1 exclusive_caps=0

echo "✅ Module v4l2loopback prêt. Vérification :"
ls -l /dev/video*

echo "💡 Le périphérique virtuel /dev/video1 est maintenant disponible."
