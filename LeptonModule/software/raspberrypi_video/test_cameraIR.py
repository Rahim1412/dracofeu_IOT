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

while True:
    frame = cam.capture_frame()
    if frame is None:
        continue

    cv2.imshow("Flux IR (CameraIR)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cv2.destroyAllWindows()

# ---------------------------------------------------------
# 6) Arrêt du flux
# ---------------------------------------------------------
print("🛑 Arrêt du flux thermique...")
cam.stop_cam()

print("✅ Test complet terminé !")
