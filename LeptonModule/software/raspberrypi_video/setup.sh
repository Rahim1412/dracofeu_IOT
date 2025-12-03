#!/bin/bash
# =====================================================
# setup.sh — Installation initiale du module FLIR Lepton
# (à lancer une seule fois, ou après modification du code C++)
# =====================================================

set -e  # stoppe le script si une commande échoue

# Dossier où se trouve ce script (ici: .../LeptonModule/software/raspberrypi_video)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
LEPTON_DIR="$SCRIPT_DIR"
LEPTON_BIN="$LEPTON_DIR/lepton_capture"

echo "🚀 Script d'installation du module FLIR Lepton"

# 1) Activation SPI / I2C (normalement à faire qu'une seule fois)
if [ -f /boot/firmware/config.txt ]; then
    echo "🔧 Configuration SPI/I2C dans /boot/firmware/config.txt..."
    sudo sed -i '/^dtparam=i2c_arm=/d' /boot/firmware/config.txt
    sudo sed -i '/^dtparam=spi=/d' /boot/firmware/config.txt
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    echo "dtparam=spi=on"     | sudo tee -a /boot/firmware/config.txt
else
    echo "⚠️ /boot/firmware/config.txt introuvable (selon l’OS ça peut être /boot/config.txt)."
fi

# 2) Installation des paquets nécessaires (si pas déjà faits)
echo "📦 Installation des dépendances (si nécessaire)..."
sudo apt-get update -y
sudo apt-get install -y build-essential qtbase5-dev qt5-qmake git

# 3) Compilation de lepton_capture (uniquement si pas déjà compilé)
if [ -x "$LEPTON_BIN" ]; then
    echo "✅ lepton_capture déjà compilé : $LEPTON_BIN"
    echo "   -> Pas besoin de recompiler. Si tu modifies le code C++, supprime le binaire et relance setup.sh."
    exit 0
fi

echo "🧱 Compilation de lepton_capture..."
cd "$LEPTON_DIR" || {
  echo "❌ Dossier $LEPTON_DIR introuvable."
  exit 1
}

qmake lepton_capture.pro
make -j4

if [ -x "$LEPTON_BIN" ]; then
    echo "✅ Compilation terminée. Binaire disponible : $LEPTON_BIN"
else
    echo "❌ Erreur : le binaire lepton_capture n'a pas été généré."
    exit 1
fi

echo "ℹ️ Si tu viens de modifier /boot/firmware/config.txt, un redémarrage de la Raspberry Pi peut être nécessaire."
