from CameraIR import *

cam = CameraIR()

cam.start_cam()

print("Capture image Lepton...")
frame = cam.capture_lepton_frame("/dev/video1")  # retourne une image numpy (grayscale uint8)
print(frame.shape, frame.dtype)              # ex: (120, 160) uint8 pour Lepton

# (optionnel) sauvegarder pour vérifier
cv2.imwrite("/home/dracofeu/dracofeu_IOT/LeptonModule/test_lepton.jpg", frame)

cam.stop_cam()
