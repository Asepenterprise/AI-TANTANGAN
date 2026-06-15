import cv2
import time

# KAMERA DULU
cap = cv2.VideoCapture(0)
time.sleep(2)

import mediapipe as mp
import numpy as np

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

plank_aktif = False
plank_mulai = None
plank_total = 0
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

    cv2.rectangle(frame, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.putText(frame, "PLANK TIMER", (10, 40),
               cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    if hasil and hasil.pose_landmarks:
        mp_draw.draw_landmarks(
            frame, hasil.pose_landmarks, mp_pose.POSE_CONNECTIONS)

        lm = hasil.pose_landmarks.landmark

        bahu = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
        pinggul = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                  lm[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
        lutut = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]

        sudut_tubuh = hitung_sudut(bahu, pinggul, lutut)

        sekarang = time.time()

        if sudut_tubuh > 160:
            if not plank_aktif:
                plank_aktif = True
                plank_mulai = sekarang

            durasi = sekarang - plank_mulai
            plank_total = durasi
            menit = int(durasi // 60)
            detik = int(durasi % 60)

            # Hitung posisi tengah teks
            teks_timer = f"PLANK: {menit:02d}:{detik:02d}"
            ukuran = cv2.getTextSize(teks_timer, cv2.FONT_HERSHEY_SIMPLEX, 2, 3)[0]
            x_tengah = (w - ukuran[0]) // 2

            cv2.putText(frame, teks_timer,
                         (x_tengah, h//2),
                          cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
            cv2.putText(frame, "POSISI BAGUS!",
                        (x_tengah, h//2 + 60),
                          cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
           

        else:
            plank_aktif = False
            if plank_total > 0:
                menit = int(plank_total // 60)
                detik = int(plank_total % 60)
                cv2.putText(frame, f"HASIL: {menit:02d}:{detik:02d}",
                           (w//2-150, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
            cv2.putText(frame, "Masuk posisi plank untuk mulai",
                       (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

        cv2.putText(frame, f"Sudut: {int(sudut_tubuh)}",
                   (10, h-50),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('Plank Timer', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()