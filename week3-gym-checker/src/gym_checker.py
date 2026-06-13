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

pushup_counter = 0
squat_counter = 0
pushup_status = "UP"
squat_status = "UP"
mode = "PUSHUP"
frame_count = 0
hasil = None

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

    # Header
    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, f"MODE: {mode}", (10, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    cv2.putText(frame, "P=PushUp  S=Squat  Q=Keluar", (w-320, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    if hasil and hasil.pose_landmarks:
        mp_draw.draw_landmarks(
            frame, hasil.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        lm = hasil.pose_landmarks.landmark

        if mode == "PUSHUP":
            bahu = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                    lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            siku = [lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].x * w,
                    lm[mp_pose.PoseLandmark.LEFT_ELBOW.value].y * h]
            pergelangan = [lm[mp_pose.PoseLandmark.LEFT_WRIST.value].x * w,
                          lm[mp_pose.PoseLandmark.LEFT_WRIST.value].y * h]

            sudut = hitung_sudut(bahu, siku, pergelangan)

            if sudut < 90:
                pushup_status = "DOWN"
            elif sudut > 160 and pushup_status == "DOWN":
                pushup_status = "UP"
                pushup_counter += 1

            cv2.putText(frame, f"Push-up: {pushup_counter}", (10, h-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(frame, pushup_status, (w-150, h-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
            cv2.putText(frame, f"{int(sudut)}°",
                       (int(siku[0]), int(siku[1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        elif mode == "SQUAT":
            pinggul = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                      lm[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
            lutut = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                    lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]
            pergelangan_kaki = [lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].x * w,
                               lm[mp_pose.PoseLandmark.LEFT_ANKLE.value].y * h]

            sudut = hitung_sudut(pinggul, lutut, pergelangan_kaki)

            if sudut < 140:
                squat_status = "DOWN"
            elif sudut > 160 and squat_status == "DOWN":
                squat_status = "UP"
                squat_counter += 1

            cv2.putText(frame, f"Squat: {squat_counter}", (10, h-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            cv2.putText(frame, squat_status, (w-150, h-60),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
            cv2.putText(frame, f"{int(sudut)}°",
                       (int(lutut[0]), int(lutut[1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('AI Gym Checker', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord('p'):
        mode = "PUSHUP"
        pushup_counter = 0
        pushup_status = "UP"
    elif key == ord('s'):
        mode = "SQUAT"
        squat_counter = 0
        squat_status = "UP"

cap.release()
cv2.destroyAllWindows()