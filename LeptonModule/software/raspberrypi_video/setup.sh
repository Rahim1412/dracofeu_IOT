#!/bin/bash
# =====================================================
# Script d'installation et de compilation forcée du backend FLIR Lepton 3.5
# =====================================================

set -e  # stoppe le script si erreur

echo "🚀 [1/4] Activation de I2C et SPI..."
if [ -f /boot/firmware/config.txt ]; then
    sudo sed -i '/^dtparam=i2c_arm=/d' /boot/firmware/config.txt
    sudo sed -i '/^dtparam=spi=/d' /boot/firmware/config.txt
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
else
    echo "⚠️ Aucun fichier /boot/firmware/config.txt trouvé (OS différent ?)"
fi

echo "📦 [2/4] Installation des dépendances..."
sudo apt-get update -y
sudo apt-get install -y build-essential qtbase5-dev qt5-qmake git

# ============================
# 🧱 [3/4] Compilation forcée du projet lepton_capture
# ============================

# Dossier où se trouve ce script (raspberrypi_video)
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
VIDEO_DIR="$SCRIPT_DIR"
BIN_PATH="$VIDEO_DIR/lepton_capture"

echo "🧹 Suppression de l'ancien binaire (si présent)..."
rm -f "$BIN_PATH"

echo "🔧 Compilation forcée du backend lepton_capture..."
cd "$VIDEO_DIR"

# Nettoyage des anciens fichiers de build Qt
rm -rf gen_mocs gen_objs Makefile .qmake.stash

# Regénération des fichiers et compilation
qmake lepton_capture.pro
make -j4

if [ ! -f "$BIN_PATH" ]; then
    echo "❌ Erreur : compilation échouée, binaire introuvable"
    exit 1
fi

echo "✅ Compilation terminée : $BIN_PATH"

echo "🎉 [4/4] Installation terminée."
echo "➡️ Redémarre la Raspberry Pi pour finaliser l’activation SPI/I2C (si ce n'est pas déjà fait)."
