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

    def capture_lepton_frame(self, device="/dev/video1", to_uint8=True, timeout_s=2.0):

        cap = None
        try:
            # Ouvre uniquement le device Lepton
            cap = cv2.VideoCapture(device)  # éviter CAP_V4L2 qui peut bug selon build
            if not cap.isOpened():
                raise RuntimeError(f"Impossible d'ouvrir {device}. Vérifie start.sh et les droits (groupe 'video').")

            # Réduit la latence si supporté (certaines builds ignorent cette prop, pas grave)
            try:
                cap.set(cv2.CAP_PROP_BUFFERSIZE, 1)
            except Exception:
                pass

            # Boucle de lecture avec timeout dur
            deadline = time.monotonic() + timeout_s
            frame = None
            while time.monotonic() < deadline:
                ok, fr = cap.read()
                if ok and fr is not None:
                    frame = fr
                    break
                time.sleep(0.01)  # petite pause non bloquante

            if frame is None:
                raise RuntimeError(f"Aucune frame reçue sous {timeout_s:.1f}s (flux vide ?)")

            # Normalisation en niveaux de gris
            if len(frame.shape) == 3 and frame.shape[2] == 3:
                frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

            # Lepton Y16 -> uint8
            if to_uint8 and frame.dtype == np.uint16:
                lo = np.percentile(frame, 2)
                hi = np.percentile(frame, 98)
                if hi <= lo:
                    lo, hi = frame.min(), frame.max()
                    if hi == lo:
                        hi = lo + 1
                frame = np.clip((frame - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)

            return frame

        finally:
            if cap is not None:
                cap.release()
