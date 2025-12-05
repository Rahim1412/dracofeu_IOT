import subprocess
import os
import time
import cv2
import numpy as np
import piexif
from PIL import Image
import io


class CameraIR:
    """
    Interface haut-niveau pour la caméra FLIR Lepton.
    - start_cam / stop_cam : pilotent le backend C++ via les scripts Bash
    - capture_frame        : lit la dernière image /tmp/lepton_last.png
    - save_image           : sauvegarde une image dans un fichier JPG
    - add_gps_exif         : ajoute les infos GPS dans une image
    """

    def __init__(self):
        # Dossiers de travail
        self.base_dir = "/home/dracofeu/dracofeu_IOT/LeptonModule"
        self.rpi_video_dir = os.path.join(
            self.base_dir, "software/raspberrypi_video"
        )

        # Scripts Bash
        self.init_path = os.path.join(self.rpi_video_dir, "init.sh")
        self.start_path = os.path.join(self.rpi_video_dir, "start.sh")
        self.stop_path = os.path.join(self.rpi_video_dir, "stop.sh")

        # Fichier produit par le backend C++
        self.capture_path = "/tmp/lepton_last.png"

        # Lancement de l'init une seule fois
        self._run_script(self.init_path)

    # ------------------------------------------------------------------
    # OUTILS INTERNES
    # ------------------------------------------------------------------
    def _run_script(self, script_full):
        """Exécute un script Bash depuis un chemin absolu."""

        if not os.path.isfile(script_full):
            print(f"❌ Script introuvable : {script_full}")
            return

        try:
            # On s'assure que le script est exécutable
            os.chmod(script_full, 0o755)

            result = subprocess.run(
                ["bash", script_full],
                capture_output=True,
                text=True
            )

            print(f"✅ Script exécuté : {script_full}")
            if result.stdout:
                print("STDOUT:")
                print(result.stdout.strip())
            if result.stderr:
                print("⚠️ STDERR:")
                print(result.stderr.strip())

        except Exception as e:
            print(f"❌ Erreur lors de l'exécution de {script_full} : {e}")

    def _wait_first_frame(self, timeout=5.0):
        """
        Attend que /tmp/lepton_last.png soit lisible par OpenCV.
        Retourne True si une image a pu être lue, False sinon.
        """
        print("⏳ Attente de la première image lisible...")

        t0 = time.time()
        while time.time() - t0 < timeout:
            if not os.path.exists(self.capture_path):
                time.sleep(0.1)
                continue

            img = cv2.imread(self.capture_path, cv2.IMREAD_UNCHANGED)
            if img is not None:
                print("✅ Première image lue.")
                return True

            time.sleep(0.1)

        print("❌ Impossible de lire la première image. Le flux n'est peut-être pas lancé.")
        return False

    # ------------------------------------------------------------------
    # CONTROLE DU BACKEND
    # ------------------------------------------------------------------
    def start_cam(self):
        """
        Démarre le backend C++ (lepton_capture) via start.sh
        et attend la première image.
        """
        print("▶️ Démarrage de la caméra IR...")
        try:
            self._run_script(self.start_path)
            self._wait_first_frame()
        except Exception as e:
            print(f"❌ Erreur lors du démarrage de la caméra : {e}")

    def stop_cam(self):
        """Arrête le backend C++ via stop.sh."""
        print("⛔ Arrêt de la caméra IR...")
        try:
            self._run_script(self.stop_path)
        except Exception as e:
            print(f"❌ Erreur lors de l'arrêt de la caméra : {e}")

    # ------------------------------------------------------------------
    # CAPTURE / LECTURE D'IMAGE
    # ------------------------------------------------------------------
    def capture_frame(self, normalize=False, retry_delay=0.01):
        """
        Lit la dernière image /tmp/lepton_last.png.
        Si l'image est absente ou en cours d'écriture, réessaie en boucle
        jusqu'à obtenir une frame valide.

        retry_delay : temps en secondes entre deux tentatives (par défaut : 10 ms)
        """

        while True:
            # Le fichier existe ?
            if not os.path.exists(self.capture_path):
                time.sleep(retry_delay)
                continue

            # Lecture OpenCV
            img = cv2.imread(self.capture_path, cv2.IMREAD_UNCHANGED)

            # Image illisible → le backend est peut-être en train d'écrire
            if img is None:
                time.sleep(retry_delay)
                continue

            # Conversion couleur → gris
            if img.ndim == 3:
                img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

            # Normalisation optionnelle
            if not normalize:
                return img

            img_f = img.astype(np.float32)
            minv = img_f.min()
            maxv = img_f.max()

            if maxv > minv:
                img_norm = (img_f - minv) / (maxv - minv)
            else:
                img_norm = np.zeros_like(img_f, dtype=np.float32)

            return img_norm


    def save_image(self):
        """
        Capture l'image actuelle et l'enregistre sous la forme
        photo_1.jpg, photo_2.jpg, etc. dans le dossier LeptonModule.
        Retourne le chemin du fichier créé ou None en cas d'échec.
        """
        img = self.capture_frame(normalize=False)
        if img is None:
            print("❌ Impossible de capturer l'image pour sauvegarde.")
            return None

        base_dir = self.base_dir
        base_name = "photo"
        ext = ".jpg"

        # Cherche le prochain numéro disponible
        i = 1
        while os.path.exists(os.path.join(base_dir, f"{base_name}_{i}{ext}")):
            i += 1

        save_path = os.path.join(base_dir, f"{base_name}_{i}{ext}")

        # Sauvegarde en JPG
        if cv2.imwrite(save_path, img):
            print(f"📸 Photo sauvegardée : {save_path}")
            return save_path
        else:
            print("❌ Erreur lors de l'écriture du fichier image.")
            return None

    # ------------------------------------------------------------------
    # GPS / EXIF
    # ------------------------------------------------------------------
    def dms_to_deg(self, value, ref):
        d, m, s = value
        deg = d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600
        if ref in ['S', 'W']:
            deg = -deg
        return deg

    def deg_to_dms_rational(self, deg_float):
        deg = int(deg_float)
        min_float = (deg_float - deg) * 60
        minutes = int(min_float)
        sec_float = (min_float - minutes) * 60
        return ((deg, 1), (minutes, 1), (int(sec_float * 100), 100))

    def add_gps_exif(self, image_path, lat, lon, alt):
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: self.deg_to_dms_rational(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: self.deg_to_dms_rational(abs(lon)),
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (int(alt * 100), 100),
        }

        exif_dict = {"GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)

        img = Image.open(image_path)
        img.save(image_path, exif=exif_bytes)
        print(f"📌 GPS ajouté à {image_path}")

    # ------------------------------------------------------------------
    # MODE APERCU / STREAM (optionnel)
    # ------------------------------------------------------------------
    def preview_stream(self, window_name="Flux IR (CameraIR)", key_quit='q'):
        """
        Affiche un aperçu du flux IR dans une fenêtre OpenCV.
        Ne démarre ni n'arrête la caméra : suppose que start_cam()
        a déjà été appelé auparavant.
        """
        print("🎥 Aperçu du flux IR (CameraIR.preview_stream)")
        print("➡️ Appuie sur 'q' pour quitter.")

        if not self._wait_first_frame(timeout=5.0):
            return

        while True:
            img = self.capture_frame(normalize=False)
            if img is None:
                # image non lisible à cet instant, on saute cette frame
                time.sleep(0.01)
                continue

            cv2.imshow(window_name, img)

            if cv2.waitKey(1) & 0xFF == ord(key_quit):
                break

        cv2.destroyAllWindows()
        print("🛑 Fenêtre stream fermée.")


# Exemple d'utilisation simple
if __name__ == "__main__":
    cam = CameraIR()
    cam.start_cam()
    cam.preview_stream()
    cam.stop_cam()
