import os
import subprocess
import cv2

# -------------------------------------------------------------
# 📌 Paramètres
# -------------------------------------------------------------
device = "/dev/video1"
base_dir = "/home/dracofeu/dracofeu_IOT/LeptonModule/capture"

os.makedirs(base_dir, exist_ok=True)

base_name = "photo"
ext = ".jpg"

# Trouver le numéro suivant
i = 1
while os.path.exists(os.path.join(base_dir, f"{base_name}_{i}{ext}")):
    i += 1

save_path = os.path.join(base_dir, f"{base_name}_{i}{ext}")

# -------------------------------------------------------------
# 📸 Capture via ffmpeg
# -------------------------------------------------------------
print(f"📸 Capture {i} ...")

cmd = [
    "ffmpeg",
    "-y",
    "-f", "video4linux2",
    "-video_size", "160x120",
    "-i", device,
    "-frames:v", "1",
    save_path
]

try:
    subprocess.run(cmd, check=True)
    print(f"✅ Photo sauvegardée : {save_path}")
except subprocess.CalledProcessError:
    print("❌ Erreur : capture impossible.")
    exit()

# -------------------------------------------------------------
# 🔥 Charger dans OpenCV
# -------------------------------------------------------------
img = cv2.imread(save_path)

if img is None:
    print("❌ Impossible de lire l'image.")
else:
    print("📷 Image chargée :", img.shape)

    cv2.imshow("Capture Lepton", img)
    cv2.waitKey(0)
    cv2.destroyAllWindows()
