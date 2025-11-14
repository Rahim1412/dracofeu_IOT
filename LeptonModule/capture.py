import cv2
import os

device = "/dev/video1"
save_dir = "/home/dracofeu/dracofeu_IOT/LeptonModule/capture"
os.makedirs(save_dir, exist_ok=True)
save_path = os.path.join(save_dir, "test_opencv.jpg")

print(f"[INFO] Ouverture de {device} ...")
cap = cv2.VideoCapture(device, cv2.CAP_V4L2)  # on force V4L2

if not cap.isOpened():
    print("❌ cap.isOpened() = False")
    raise SystemExit

print("[INFO] Lecture d'une frame ...")
ret, frame = cap.read()
cap.release()

print(f"[INFO] ret={ret}, frame is None? {frame is None}")

if not ret or frame is None:
    print("❌ Impossible de lire une image.")
    raise SystemExit

print(f"[INFO] frame.shape = {frame.shape}, dtype = {frame.dtype}")

ok = cv2.imwrite(save_path, frame)
print("✅ Image sauvegardée ?" , ok, "→", save_path)
