from CameraIR import *
from time import sleep

cam = CameraIR()
cam.start_cam()

for i in range(5):
    print(f"📸 Photo {i+1}/100 ...")
    cam.capture_image()   # ta fonction qui sauvegarde automatiquement avec un numéro

    print("attendre 1 seconde...")
    sleep(1)  # Petite pause entre les captures

print("✔️ 5 photos prises.")
cam.stop_cam()

