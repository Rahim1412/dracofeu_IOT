def capture_camera_rpi4(self):
        """
        Capture une image depuis la caméra Pi 4 déjà démarrée.
        Ne stoppe pas la caméra après la capture.
        """
        if not hasattr(self, "_camera4_started") or not self._camera4_started:
            raise RuntimeError("La caméra Pi 4 n’est pas démarrée. Appeler start_camera_rpi4() d'abord.")

        if not self.camera_rpi4.isOpened():
            raise RuntimeError("Flux caméra Pi 4 non accessible")

        ret, frame = self.camera_rpi4.read()
        if not ret or frame is None:
            raise RuntimeError("Impossible de capturer une image avec la caméra Pi 4")

        self.log({"event": "Image capturée depuis la Pi 4"}, log_name="default.json")

        return frame
    

    def dms_to_deg(value, ref):
        """Convertit les coordonnées DMS EXIF en degrés décimaux."""
        d, m, s = value
        deg = d[0]/d[1] + (m[0]/m[1])/60 + (s[0]/s[1])/3600
        if ref in ['S', 'W']:
            deg = -deg
        return deg

    def get_gps_from_exif(image_path):
        """Extrait latitude, longitude et altitude (en mètres) depuis les métadonnées EXIF."""
        exif_dict = piexif.load(image_path)
        gps = exif_dict.get("GPS", {})
        if not gps:
            return None, None, None

        try:
            lat = dms_to_deg(gps[piexif.GPSIFD.GPSLatitude], gps[piexif.GPSIFD.GPSLatitudeRef].decode())
            lon = dms_to_deg(gps[piexif.GPSIFD.GPSLongitude], gps[piexif.GPSIFD.GPSLongitudeRef].decode())
            alt_ref = gps.get(piexif.GPSIFD.GPSAltitudeRef, 0)
            alt = gps.get(piexif.GPSIFD.GPSAltitude, (0, 1))
            altitude = alt[0] / alt[1]
            if alt_ref == 1:  # sous le niveau de la mer
                altitude = -altitude
            return lat, lon, altitude
        except Exception:
            return None, None, None
    
    def deg_to_dms_rational(deg_float):
        deg = int(deg_float)
        min_float = (deg_float - deg) * 60
        minutes = int(min_float)
        sec_float = (min_float - minutes) * 60
        return ((deg, 1), (minutes, 1), (int(sec_float * 100), 100))


    def add_gps_exif(image_path, lat, lon, alt):
        gps_ifd = {
            piexif.GPSIFD.GPSLatitudeRef: 'N' if lat >= 0 else 'S',
            piexif.GPSIFD.GPSLatitude: deg_to_dms_rational(abs(lat)),
            piexif.GPSIFD.GPSLongitudeRef: 'E' if lon >= 0 else 'W',
            piexif.GPSIFD.GPSLongitude: deg_to_dms_rational(abs(lon)),
            piexif.GPSIFD.GPSAltitudeRef: 0,
            piexif.GPSIFD.GPSAltitude: (int(alt * 100), 100),
        }

        exif_dict = {"GPS": gps_ifd}
        exif_bytes = piexif.dump(exif_dict)

        img = Image.open(image_path)
        img.save(image_path, exif=exif_bytes)

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