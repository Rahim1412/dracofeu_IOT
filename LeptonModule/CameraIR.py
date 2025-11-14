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
    def capture_image(self):
        """
        Capture une image depuis le flux vidéo Lepton
        et enregistre le fichier sous un nom unique : photo_1.jpg, photo_2.jpg, etc.
        """
        base_dir = "/home/dracofeu/dracofeu_IOT/LeptonModule"
        base_name = "photo"
        ext = ".jpg"

        # Cherche le prochain numéro disponible
        i = 1
        while os.path.exists(f"{base_dir}/{base_name}_{i}{ext}"):
            i += 1

        save_path = f"{base_dir}/{base_name}_{i}{ext}"

        cmd = [
            "ffmpeg",
            "-y",
            "-f", "video4linux2",
            "-input_format", "Y16",
            "-video_size", "160x120",
            "-i", self.device,
            "-frames:v", "1",
            save_path
        ]

        print(f"📸 Capture {i} ...")
        try:
            subprocess.run(cmd, check=True)
            print(f"✅ Photo sauvegardée : {save_path}")
        except subprocess.CalledProcessError:
            print("❌ Erreur : capture impossible.")

    def capture_image_opencv(self):
        """Capture une image depuis le flux vidéo Lepton et enregistre le fichier sous un nom unique : photo_1.jpg, photo_2.jpg, etc.(version OpenCV)"""
        # Dossier de destination
        base_dir = "/home/dracofeu/dracofeu_IOT/LeptonModule/capture"
        os.makedirs(base_dir, exist_ok=True)

        base_name = "photo"
        ext = ".jpg"

        # Cherche le prochain numéro disponible
        i = 1
        while os.path.exists(os.path.join(base_dir, f"{base_name}_{i}{ext}")):
            i += 1

        save_path = os.path.join(base_dir, f"{base_name}_{i}{ext}")
        print(f"📸 Capture {i} ...")

        # Ouvre la caméra (self.device doit = "/dev/video1")
        cap = cv2.VideoCapture(self.device)

        if not cap.isOpened():
            print(f"❌ Impossible d'ouvrir {self.device}")
            return

        # Lit UNE image
        ret, frame = cap.read()
        cap.release()

        if not ret or frame is None:
            print("❌ Impossible de lire une image depuis la caméra.")
            return

        # Sauvegarde l'image
        if cv2.imwrite(save_path, frame):
            print(f"✅ Photo sauvegardée : {save_path}")
        else:
            print("❌ Erreur lors de la sauvegarde de l'image.")
