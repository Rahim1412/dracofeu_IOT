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

    def capture_lepton_frame(device="/dev/video1", to_uint8=True, tries=5):
        """
        Ouvre le flux vidéo V4L2 (ex: /dev/video1), lit une frame et la retourne.
        - Si la frame est en 16 bits (Lepton Y16), conversion optionnelle vers uint8 (contraste auto).
        - 'tries' = nombre d'essais de lecture (les 1ères frames peuvent être nulles).
        
        Retour:
            frame (np.ndarray)  # grayscale uint8 si to_uint8=True, sinon dtype d'origine
        Lève:
            RuntimeError en cas d'échec.
        """
        # Ouvrir le device V4L2
        cap = cv2.VideoCapture(device, cv2.CAP_V4L2)
        if not cap.isOpened():
            # Essai par index 1 au cas où
            cap = cv2.VideoCapture(1, cv2.CAP_V4L2)
            if not cap.isOpened():
                raise RuntimeError(f"Impossible d'ouvrir le flux vidéo ({device} / index 1).")

        # Lire quelques frames pour "réchauffer" le flux
        frame = None
        for _ in range(tries):
            ok, fr = cap.read()
            if ok and fr is not None:
                frame = fr
                break
            cv2.waitKey(10)  # petite pause

        cap.release()

        if frame is None:
            raise RuntimeError("Lecture de frame échouée (flux indisponible ou vide).")

        # Si OpenCV renvoie BGR (3 canaux), on convertit en grayscale
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # Gestion du 16 bits (Lepton Y16) → conversion optionnelle vers 8 bits
        if to_uint8 and frame.dtype == np.uint16:
            # Échelle robuste (2%–98%) pour un bon contraste
            lo = np.percentile(frame, 2)
            hi = np.percentile(frame, 98)
            if hi <= lo:
                lo, hi = frame.min(), frame.max()
                if hi == lo:
                    hi = lo + 1
            frame = np.clip((frame - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)

        return frame