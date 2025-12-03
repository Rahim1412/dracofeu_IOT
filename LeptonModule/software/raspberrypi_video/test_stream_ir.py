import cv2
import time
import os

CAPTURE_PATH = "/tmp/lepton_last.png"

def main():
    print("🎥 Vérification du flux IR sans démarrage automatique")
    print("➡️ Ce script n'appelle PAS start.sh ni stop.sh")
    print("➡️ Assure-toi que lepton_capture tourne déjà")

    if not os.path.exists(CAPTURE_PATH):
        print("❌ Aucun fichier /tmp/lepton_last.png trouvé.")
        print("   → Lance manuellement : ./start.sh")
        return

    print("⏳ Attente de la première image lisible...")
    t0 = time.time()
    while time.time() - t0 < 5:
        img = cv2.imread(CAPTURE_PATH, cv2.IMREAD_UNCHANGED)
        if img is not None:
            print("✅ Première image lue. Affichage du flux...")
            break
        time.sleep(0.1)
    else:
        print("❌ Impossible de lire l'image. Le flux n'est peut-être pas lancé.")
        return

    # Boucle d'affichage du stream
    while True:
        img = cv2.imread(CAPTURE_PATH, cv2.IMREAD_UNCHANGED)
        if img is None:
            continue

        # Conversion en gris si couleur
        if img.ndim == 3:
            img = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)

        cv2.imshow("Flux IR (sans start/stop)", img)

        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    cv2.destroyAllWindows()
    print("🛑 Fenêtre fermée. Aucun process arrêté (normal).")


if __name__ == "__main__":
    main()
