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
        """Capture une seule image depuis le flux vidéo Lepton et la sauvegarde."""
        cap = cv2.VideoCapture(self.device)
        if not cap.isOpened():
            print(f"❌ Impossible d'ouvrir {self.device}. Vérifie que start.sh est lancé.")
            return

        ok, frame = cap.read()
        cap.release()

        if not ok or frame is None:
            print("❌ Échec de la capture (aucune image reçue).")
            return

        # Conversion en niveaux de gris si besoin
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Conversion Y16 → uint8 si nécessaire (Lepton)
        if frame.dtype == np.uint16:
            lo, hi = np.percentile(frame, (2, 98))
            frame = np.clip((frame - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)

        cv2.imwrite(save_path, frame)
        print(f"✅ Image capturée et sauvegardée : {save_path}")
