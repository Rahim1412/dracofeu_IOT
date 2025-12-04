from CameraIR import CameraIR
import cv2
import time

cam = CameraIR()
cam.start_cam()

while True:
    frame = cam.capture_frame()
    if frame is None:
        time.sleep(0.01)
        continue

    cv2.imshow("Flux IR (via CameraIR)", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.stop_cam()
cv2.destroyAllWindows()
