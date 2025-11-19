from CameraIR import *
from time import sleep

cam = CameraIR()
cam.start_cam()

#for i in range(100):
#    print(f"📸 Photo {i+1}/100 ...")
#    cam.capture_image()   # ta fonction qui sauvegarde automatiquement avec un numéro
#
#    print("attendre 1 secondes...")
#    sleep(1)  # Petite pause entre les captures

#print("✔️ 5 photos prises.")
#path = cam.capture_image() 
#cam.add_gps_exif(path, lat=48.8566, lon=2.3522, alt=35)
cam.record_video(10)
cam.stop_cam()

