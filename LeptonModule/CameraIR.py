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

    def capture_lepton_frame(self, device="/dev/video1", to_uint8=True, tries=5):
        import cv2, numpy as np, os

        # 1) Liste d’essais (backend + device)
        candidates = []
        # a) chemin direct, sans backend
        candidates.append(("path_no_api", lambda: cv2.VideoCapture(device)))
        # b) chemin direct, backend V4L2
        candidates.append(("path_v4l2",  lambda: cv2.VideoCapture(device, cv2.CAP_V4L2)))
        # c) index 1, backend V4L2
        candidates.append(("index1_v4l2", lambda: cv2.VideoCapture(1, cv2.CAP_V4L2)))
        # d) index 1, sans backend
        candidates.append(("index1_no_api", lambda: cv2.VideoCapture(1)))
        # e) index 0 (au cas où), V4L2
        candidates.append(("index0_v4l2", lambda: cv2.VideoCapture(0, cv2.CAP_V4L2)))
        # f) index 0 sans backend
        candidates.append(("index0_no_api", lambda: cv2.VideoCapture(0)))

        cap = None
        last_reason = "inconnu"
        for name, opener in candidates:
            try:
                cap = opener()
                if cap is not None and cap.isOpened():
                    # trouvé !
                    # print(f"[INFO] Ouverture OK via {name}")
                    break
                else:
                    last_reason = f"{name}: cap non ouvert"
                    if cap is not None:
                        cap.release()
                    cap = None
            except Exception as e:
                last_reason = f"{name}: {e}"
                cap = None

        if cap is None:
            raise RuntimeError(
                "Impossible d'ouvrir la caméra. "
                f"Dernière tentative: {last_reason}. "
                "Vérifie que /dev/video1 existe, que le flux est lancé, et les droits (groupe 'video')."
            )

        # 2) Lecture de quelques frames (warm-up)
        frame = None
        for _ in range(tries):
            ok, fr = cap.read()
            if ok and fr is not None:
                frame = fr
                break
            cv2.waitKey(10)

        cap.release()

        if frame is None:
            raise RuntimeError("Lecture de frame échouée (flux indisponible ou vide).")

        # 3) Normalisation en niveaux de gris 8 bits
        if len(frame.shape) == 3 and frame.shape[2] == 3:
            frame = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        if to_uint8 and frame.dtype == np.uint16:
            lo = np.percentile(frame, 2)
            hi = np.percentile(frame, 98)
            if hi <= lo:
                lo, hi = frame.min(), frame.max()
                if hi == lo:
                    hi = lo + 1
            frame = np.clip((frame - lo) * (255.0 / (hi - lo)), 0, 255).astype(np.uint8)

        return frame
