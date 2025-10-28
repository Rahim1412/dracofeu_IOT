#!/bin/bash
# =====================================================
# Script d'installation et de configuration du projet FLIR Lepton 3.5
# =====================================================

set -e  # stoppe le script si une commande échoue

echo "🚀 [1/4] Activation de I2C et SPI dans /boot/firmware/config.txt..."
if [ -f /boot/firmware/config.txt ]; then
    sudo sed -i '/^dtparam=i2c_arm=/d' /boot/firmware/config.txt
    sudo sed -i '/^dtparam=spi=/d' /boot/firmware/config.txt
    echo "dtparam=i2c_arm=on" | sudo tee -a /boot/firmware/config.txt
    echo "dtparam=spi=on" | sudo tee -a /boot/firmware/config.txt
else
    echo "⚠️ Fichier /boot/firmware/config.txt introuvable, vérifie ton OS (peut être /boot/config.txt)"
fi

echo "📦 [2/4] Installation des dépendances..."
sudo apt-get update -y
sudo apt-get install -y cmake libv4l-dev v4l-utils v4l2loopback-dkms build-essential git

echo "🧱 [3/4] Compilation du projet v4l2lepton..."
cd "$(dirname "$0")/software/v4l2lepton" || {
  echo "❌ Dossier software/v4l2lepton introuvable."
  exit 1
}
make clean && make

echo "✅ Compilation terminée."

echo "[4/4] I2C et SPI activés, dépendances installées."
echo "Veuillez redémarrer votre raspberry pi pour appliquer les modifications."
