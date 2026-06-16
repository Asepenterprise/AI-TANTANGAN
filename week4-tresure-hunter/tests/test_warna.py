import cv2
import numpy as np
import time

cap = cv2.VideoCapture(0)
time.sleep(2)  # ← tambahkan ini

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    cv2.imshow('Kalibrasi', frame)

    def klik(event, x, y, flags, param):
        if event == cv2.EVENT_LBUTTONDOWN:
            print(f"HSV: {hsv[y,x]}")

    cv2.setMouseCallback('Kalibrasi', klik)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()