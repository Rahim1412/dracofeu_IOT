from CameraIR import CameraIR

cam = CameraIR()
cam.start_cam()

while True:
    frame = cam.capture_frame()
    if frame is None:
        continue

    cv2.imshow("Flux IR (via CameraIR)", frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cam.stop_cam()
cv2.destroyAllWindows()