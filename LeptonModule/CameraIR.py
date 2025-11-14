import subprocess
import os
import cv2
import numpy as np

class CameraIR:

    def __init__(self):
        self.init_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/init.sh"
        self.start_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/start.sh"
        self.stop_path = "/home/dracofeu/dracofeu_IOT/LeptonModule/stop.sh"
        self.run(self.init_path)
        self.device = "/dev/video1"  # Périphérique vidéo pour Lepton

    def run(self, script_full):
        """Rend le script exécutable puis l'exécute depuis un chemin absolu."""

        # Vérifie si le fichier existe
        if not os.path.isfile(script_full):
            print(f"Script introuvable : {script_full}")
            return

        try:
            # Rend exécutable
            subprocess.run(["chmod", "+x", script_full], check=True)

            # Exécute le script via Bash
            result = subprocess.run(
                ["bash", script_full],
                capture_output=True,
                text=True
            )

            print("✅ Script exécuté")
            print("STDOUT:")
            print(result.stdout)

            if result.stderr:
                print("⚠️ STDERR:")
                print(result.stderr)

        except Exception as e:
            print(f" Erreur : {e}")

    def start_cam(self):
        try:
            self.run(self.start_path)

        except Exception as e:
            print(f"Erreur lors du démarrage de la caméra : {e}")

    def stop_cam(self):
        try:
            self.run(self.stop_path)

        except Exception as e:
            print(f"Erreur lors de l'arrêt de la caméra : {e}")

    def capture_image(self, save_path="/home/dracofeu/dracofeu_IOT/LeptonModule/test_lepton.jpg"):
        print("[capture] ffmpeg → 1 frame ...")
        # Si ton Lepton émet en Y16, ffmpeg saura lire, mais l’image peut paraître sombre.
        # Pour un test simple, on capture brut :
        cmd = ["ffmpeg", "-y", "-f", "video4linux2", "-i", self.device, "-frames:v", "1", save_path]
        try:
            subprocess.run(cmd, check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            print(f"✅ Image sauvegardée : {save_path}")
        except subprocess.CalledProcessError:
            print("❌ ffmpeg n'a pas réussi à capturer l'image.")

