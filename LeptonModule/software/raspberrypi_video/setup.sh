#!/bin/bash
# =====================================================
# Script d'installation et de configuration du module FLIR Lepton 3.5
# (activation SPI/I2C + compilation du backend lepton_capture)
# =====================================================

set -e  # stoppe le script si une commande échoue

SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"

echo "🚀 [1/3] Activation de I2C et SPI dans /boot/firmware/config.txt..."
if [ -f /boot/firmware/config.txt ]; then
    sudo sed -i '/^dtparam=i2c_arm=/d' /boot/firmware/config.txt
    sudo sed -i '/^dtparam=spi=/d' /boot/firmware/config.txt
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
else
    echo "⚠️ Fichier /boot/firmware/config.txt introuvable, vérifie ton OS (peut être /boot/config.txt)."
fi

echo "📦 [2/3] Installation des dépendances (Qt, build-essential)..."
sudo apt-get update -y
sudo apt-get install -y build-essential qtbase5-dev qt5-qmake git

echo "🧱 [3/3] Compilation du backend lepton_capture..."
cd "$SCRIPT_DIR/software/raspberrypi_video" || {
  echo "❌ Dossier software/raspberrypi_video introuvable."
  exit 1
}

# Génère le Makefile et compile
qmake lepton_capture.pro
make -j4

echo "✅ Compilation terminée. Binaire disponible : $SCRIPT_DIR/software/raspberrypi_video/lepton_capture"
echo "ℹ️ Pense à redémarrer la Raspberry Pi pour appliquer l'activation SPI/I2C si ce n'est pas déjà fait."
