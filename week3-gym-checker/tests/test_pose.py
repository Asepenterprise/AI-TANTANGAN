import cv2
import mediapipe as mp
import numpy as np

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    hasil = pose.process(rgb)

    if hasil.pose_landmarks:
        mp_draw.draw_landmarks (
            frame,
            hasil.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        landmarks = hasil.pose_landmarks.landmark

        bahu_kiri = landmarks[mp_pose.PoseLandmark.LEFT_SHOULDER.value]
        print(f"Bahu kiri: x={bahu_kiri.x:.2f}, y={bahu_kiri.y:.2f}")

        bahu_kanan = landmarks[mp_pose.PoseLandmark.RIGHT_SHOULDER.value]
        print(f"Bahu Kanan: x={bahu_kanan.x:.2f}, y={bahu_kanan.y:2f}")

        h, w, _ = frame.shape

        bahu_kiri_px = (int(bahu_kiri.x * w), int(bahu_kiri.y * h))
        bahu_kanan_px = (int(bahu_kanan.x * w), int(bahu_kanan.y *h))
        
        cv2.putText(frame, f"L: {bahu_kiri_px}", bahu_kiri_px,
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)
        
        cv2.putText(frame, f"R: {bahu_kanan_px}", bahu_kanan_px,
                   cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        cv2.imshow('frame detection', frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
               break
cap.release()
cv2.destroyAllWindows()
