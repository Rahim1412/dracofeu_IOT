from CameraIR import *

cam = CameraIR()
cam.start_cam()

for i in range(5):
    print(f"📸 Photo {i+1}/100 ...")
    cam.capture_image()   # ta fonction qui sauvegarde automatiquement avec un numéro
                        
print("✔️ 100 photos prises.")
cam.stop_cam()

