import cv2
import mediapipe as mp
import numpy as np
import time
import pygame
from gtts import gTTS
import threading
import os

cap = cv2.VideoCapture(0)
time.sleep(2)

# Inisialisasi suara
pygame.mixer.init()

def hitung_sudut(a, b, c):
    a = np.array(a)
    b = np.array(b)
    c = np.array(c)
    ba = a - b
    bc = c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    sudut = np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))
    return sudut

def speak(teks):
    def play():
        try:
            tts = gTTS(text=teks, lang='id')
            tts.save("temp_gym.mp3")
            pygame.mixer.music.load("temp_gym.mp3")
            pygame.mixer.music.play()
        except:
            pass
    threading.Thread(target=play).start()

def cek_form_pushup(sudut_punggung):
    if sudut_punggung < 155:
        return "PUNGGUNG TERLALU TINGGI!", (0, 0, 255)
    else:
        return "FORM BAGUS!", (0, 255, 0)

mp_pose = mp.solutions.pose
mp_draw = mp.solutions.drawing_utils
pose = mp_pose.Pose(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5,
    model_complexity=0
)

# Variabel semua mode
pushup_counter = 0
squat_counter = 0
pushup_status = "UP"
squat_status = "UP"
plank_aktif = False
plank_mulai = None
plank_total = 0
mode = "PUSHUP"
frame_count = 0
hasil = None
suara_cooldown = 0

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    frame_count += 1
    sekarang = time.time()

    if frame_count % 2 == 0:
        rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        hasil = pose.process(rgb)

    # Background header
    cv2.rectangle(frame, (0, 0), (w, 65), (20, 20, 20), -1)
    cv2.putText(frame, f"MODE: {mode}", (10, 42),
               cv2.FONT_HERSHEY_SIMPLEX, 0.9, (0, 255, 255), 2)
    cv2.putText(frame, "P=PushUp  S=Squat  L=Plank  Q=Keluar",
               (10, 58), cv2.FONT_HERSHEY_SIMPLEX, 0.4, (200, 200, 200), 1)

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
            bahu_p = bahu
            pinggul_p = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                        lm[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
            lutut_p = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                      lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]

            sudut = hitung_sudut(bahu, siku, pergelangan)
            sudut_punggung = hitung_sudut(bahu_p, pinggul_p, lutut_p)

            if sudut < 90:
                pushup_status = "DOWN"
            elif sudut > 160 and pushup_status == "DOWN":
                pushup_status = "UP"
                pushup_counter += 1
                if sekarang > suara_cooldown:
                    speak(f"{pushup_counter}")
                    suara_cooldown = sekarang + 2

            pesan_form, warna_form = cek_form_pushup(sudut_punggung)

            cv2.rectangle(frame, (0, h-80), (w, h), (20, 20, 20), -1)
            cv2.putText(frame, f"PUSH-UP: {pushup_counter}", (10, h-45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 0), 3)
            cv2.putText(frame, pushup_status, (w-160, h-45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
            cv2.putText(frame, pesan_form, (10, h-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, warna_form, 2)
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
                if sekarang > suara_cooldown:
                    speak(f"{squat_counter}")
                    suara_cooldown = sekarang + 2

            cv2.rectangle(frame, (0, h-80), (w, h), (20, 20, 20), -1)
            cv2.putText(frame, f"SQUAT: {squat_counter}", (10, h-45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
            cv2.putText(frame, squat_status, (w-160, h-45),
                       cv2.FONT_HERSHEY_SIMPLEX, 1.5, (255, 255, 0), 3)
            cv2.putText(frame, f"{int(sudut)}°",
                       (int(lutut[0]), int(lutut[1])),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

        elif mode == "PLANK":
            bahu = [lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].x * w,
                    lm[mp_pose.PoseLandmark.LEFT_SHOULDER.value].y * h]
            pinggul = [lm[mp_pose.PoseLandmark.LEFT_HIP.value].x * w,
                      lm[mp_pose.PoseLandmark.LEFT_HIP.value].y * h]
            lutut = [lm[mp_pose.PoseLandmark.LEFT_KNEE.value].x * w,
                    lm[mp_pose.PoseLandmark.LEFT_KNEE.value].y * h]

            sudut_tubuh = hitung_sudut(bahu, pinggul, lutut)

            if sudut_tubuh > 160:
                if not plank_aktif:
                    plank_aktif = True
                    plank_mulai = sekarang

                durasi = sekarang - plank_mulai
                plank_total = durasi
                menit = int(durasi // 60)
                detik = int(durasi % 60)

                cv2.putText(frame, f"PLANK: {menit:02d}:{detik:02d}",
                           (w//2 - 180, h//2),
                           cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 255, 0), 3)
                cv2.putText(frame, "POSISI KAMU BAGUS TAHAN!", (w//2-180, h//2+60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
            else:
                plank_aktif = False
                if plank_total > 0:
                    menit = int(plank_total // 60)
                    detik = int(plank_total % 60)
                    cv2.putText(frame, f"HASIL: {menit:02d}:{detik:02d}",
                               (w//2 - 150, h//2),
                               cv2.FONT_HERSHEY_SIMPLEX, 2, (0, 0, 255), 3)
                cv2.putText(frame, "Masuk posisi plank untuk mulai",
                           (10, h//2+60),
                           cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 255), 2)

            cv2.putText(frame, f"Sudut: {int(sudut_tubuh)}°",
                       (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('Gym Checker -Asepenterprise', frame)
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
    elif key == ord('l'):
        mode = "PLANK"
        plank_aktif = False
        plank_mulai = None
        plank_total = 0

cap.release()
cv2.destroyAllWindows()