#!/bin/bash
# =====================================================
# init.sh — Initialisation de l'environnement FLIR Lepton
# (vérification du binaire + optimisation CPU)
# =====================================================

set -e

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEPTON_BIN="$SCRIPT_DIR/lepton_capture"

echo "🔍 Vérification du binaire lepton_capture..."
if [ ! -x "$LEPTON_BIN" ]; then
  echo "❌ Binaire introuvable ou non exécutable : $LEPTON_BIN"
  echo "   -> Lance d'abord ./setup.sh pour compiler le projet."
  exit 1
fi
echo "✅ lepton_capture trouvé."

echo "🧠 Configuration CPU (mode performance si possible)..."
GOV_PATH="/sys/devices/system/cpu/cpufreq/policy0/scaling_governor"
if [ -w "$GOV_PATH" ]; then
  echo performance | sudo tee "$GOV_PATH" >/dev/null || true
  echo "✅ CPU réglé en mode performance."
else
  echo "⚠️ Impossible de modifier le gouverneur CPU (pas de droits ou fichier absent)."
fi

echo "📂 Préparation du dossier /tmp pour les images..."
mkdir -p /tmp

echo "✅ Initialisation terminée."
