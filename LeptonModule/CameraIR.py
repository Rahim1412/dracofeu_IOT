import subprocess
import os
import cv2
import numpy as np
import piexif
from PIL import Image


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
            return None
        return save_path

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
