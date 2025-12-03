import cv2
import time
import os
import subprocess

# ⚠️ adapte ce chemin si besoin
BINARY_PATH = "/home/dracofeu/dracofeu_IOT/LeptonModule/software/raspberrypi_video/lepton_capture"
CAPTURE_PATH = "/tmp/lepton_last.png"


def start_backend():
    """
    Lance le programme C++ lepton_capture qui écrit en continu
    la dernière image IR dans /tmp/lepton_last.png
    """
    # On lance le process en arrière-plan, sans spammer le terminal
    proc = subprocess.Popen(
        [BINARY_PATH],
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL
    )
    return proc


def wait_for_first_image(timeout=5.0):
    """
    Attends que /tmp/lepton_last.png soit créé et lisible.
    """
    print("⏳ Attente de la première image IR...")
    t0 = time.time()
    while time.time() - t0 < timeout:
        if os.path.exists(CAPTURE_PATH):
            img = cv2.imread(CAPTURE_PATH, cv2.IMREAD_UNCHANGED)
            if img is not None:
                print("✅ Première image IR disponible")
                return True
        time.sleep(0.1)
    print("❌ Aucune image trouvée dans le délai")
    return False


def preview_stream():
    """
    Affiche le flux IR en live (lecture répétée du fichier PNG).
    Appuie sur 'q' pour quitter.
    """
    proc = start_backend()

    try:
        if not wait_for_first_image():
            proc.terminate()
            return

        print("🎥 Aperçu en live (appuie sur 'q' pour quitter)")

        while True:
            img = cv2.imread(CAPTURE_PATH, cv2.IMREAD_UNCHANGED)
            if img is None:
                continue

            # Si l'image est couleur, on la passe en niveaux de gris
            if img.ndim == 3:
                gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            else:
                gray = img

            cv2.imshow("Flux IR (lepton_capture)", gray)

            key = cv2.waitKey(1) & 0xFF
            if key == ord('q'):
                break
            elif key == ord('s'):
                # 's' pour sauvegarder une capture
                ts = time.strftime("%Y%m%d_%H%M%S")
                filename = f"capture_ir_{ts}.png"
                cv2.imwrite(filename, gray)
                print(f"💾 Image sauvegardée : {filename}")

    finally:
        cv2.destroyAllWindows()
        proc.terminate()
        try:
            proc.wait(timeout=2)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("🛑 lepton_capture arrêté")


if __name__ == "__main__":
    preview_stream()
