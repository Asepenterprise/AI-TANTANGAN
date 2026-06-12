import cv2
import mediapipe as mp
import numpy as np
import time

cap = cv2.VideoCapture(0)
time.sleep(2)

def hitung_sudut(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    sudut = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return sudut

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5, 
    min_tracking_confidence=0.5,   
    model_complexity=0             
)

frame_count = 0
hasil = None

counter = 0
status = "UP"

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_count += 1

    
    if frame_count % 2 == 0:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hasil = pose.process(rgb)

    if hasil and hasil.pose_landmarks:
        mp_draw.draw_landmarks(
            frame,
            hasil.pose_landmarks,
            mp_pose.POSE_CONNECTIONS
        )

        lm = hasil.pose_landmarks.landmark

        bahu = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
        siku = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w,
                lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
        pergelangan = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                      lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]

        sudut = hitung_sudut(bahu, siku, pergelangan)

        if sudut < 90:
            status = "DOWN"

        elif sudut > 160 and status == "DOWN":
            status = "UP"
            counter += 1
        
        cv2.putText(frame, f"Push_up: {counter}",(10, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        
        cv2.putText(frame, status, (w-150, 50),
                    cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 255, 0), 2)


        cv2.putText(frame, f"{int(sudut)}",
                   (int(siku[0]), int(siku[1])),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Sudut Sendi', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()