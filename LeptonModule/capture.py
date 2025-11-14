import cv2
import os

device = "/dev/video1"
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