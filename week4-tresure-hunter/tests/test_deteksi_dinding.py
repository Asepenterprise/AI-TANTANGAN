import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)
time.sleep(2)

lower = np.array([80, 0, 100])
upper = np.array([120, 60, 200])

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame, 1)
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)

    mask = cv2.inRange(hsv, lower, upper)

    total_pixel = frame.shape[0] * frame.shape[1]
    pixel_dinding = cv2.countNonZero(mask)
    persen = (pixel_dinding / total_pixel) * 100

    cv2.putText(frame, f"Dinding: {persen:.1f}%", (10, 50),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    if persen > 20:
        cv2.putText(frame, "DINDING TERDETEKSI!", (10, 100),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('Deteksi Dinding', frame)
    cv2.imshow('Mask', mask)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()