from CameraIR import *

cam = CameraIR()

cam.start_cam()
print("Prise de la photo...")
cam.capture_image()             # capture et enregistre une seule image
cam.stop_cam()
