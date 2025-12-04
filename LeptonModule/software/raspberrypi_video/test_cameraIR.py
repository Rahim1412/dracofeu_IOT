import time
import cv2
from CameraIR import CameraIR

print("📸 Test complet de la classe CameraIR (SANS main())")

# ---------------------------------------------------------
# 1) Initialisation de la caméra
# ---------------------------------------------------------
cam = CameraIR()
print("✅ CameraIR initialisée")

# ---------------------------------------------------------
# 2) Démarrage du flux
# ---------------------------------------------------------
print("▶️ Démarrage du flux thermique...")
cam.start_cam()
time.sleep(1)

# ---------------------------------------------------------
# 3) Test de capture de frame (numpy array)
# ---------------------------------------------------------
print("🖼️ Test capture_frame()...")

frame = cam.capture_frame()
if frame is None:
    print("❌ Aucune image reçue. Vérifie que le flux tourne.")
else:
    print("✅ Frame reçue :", frame.shape)
    cv2.imshow("Test capture_frame()", frame)
    cv2.waitKey(1000)

# ---------------------------------------------------------
# 4) Test d'enregistrement d'une photo
# ---------------------------------------------------------
print("📷 Test save_image()...")
path = cam.save_image()
if path:
    print("✅ Photo sauvegardée :", path)
else:
    print("❌ Erreur lors de la sauvegarde.")

# ---------------------------------------------------------
# 5) Test du stream continu
# ---------------------------------------------------------
print("🎥 Test du stream continu (Appuie sur Q pour quitter)")

missing_count = 0

while True:
    frame = cam.capture_frame()
    if frame is None:
        missing_count += 1
        time.sleep(0.01)   # on évite de bourriner le CPU
        # Si on n'a plus rien pendant longtemps, on sort
        if missing_count > 5000:  # ~50 s à 0.01s
            print("❌ Plus d'image disponible depuis un moment, arrêt du stream.")
            break
        continue

    missing_count = 0  # on a une image, on reset le compteur

    cv2.imshow("Flux IR (CameraIR)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()
print("🛑 Fermeture du stream.")
cam.stop_cam()


print("✅ Test complet terminé !")hhh
