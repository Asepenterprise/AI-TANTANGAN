import cv2
import mediapipe as mp
import time
import subprocess
import threading
import pygame
from gtts import gTTS
import os
import math
import numpy as np

cap = cv2.VideoCapture(0)
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

ujung_jari = [8, 12, 16, 20]
ujung_pangkal = [6, 10, 14, 18]

suara_list = {
    "intro": "audio_intro.mp3",
    "gesture_key": "audio_gesture_key.mp3",
    "scanning": "audio_scanning.mp3",
    "akses": "audio_akses.mp3",
    "vscode": "audio_vscode.mp3",
    "instagram": "audio_instagram.mp3",
    "youtube": "audio_youtube.mp3",
}

def speak(key):
    def play():
        try:
            if pygame.mixer.music.get_busy():
                return
            file = suara_list.get(key)
            if file and os.path.exists(file):
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
        except Exception as e:
            print(f"Error suara: {e}")
    threading.Thread(target=play).start()

def generate_suara():
    teks = {
        "intro": "Selamat datang tuan muda Ashraf, silakan masukkan gesture rahasia",
        "gesture_key": "Ahh tuan muda bisa aja serius love nya untuk aku, aku terima, silakan scanning untuk masuk",
        "scanning": "Sedang memindai tangan tuan muda",
        "akses": "Akses diterima, selamat datang tuan muda",
        "vscode": "Membuka V S Code",
        "instagram": "Membuka Instagram",
        "youtube": "Membuka YouTube",
    }
    pygame.mixer.init()
    print("Generating suara...")
    for key, text in teks.items():
        file = suara_list[key]
        if not os.path.exists(file):
            tts = gTTS(text=text, lang='id')
            tts.save(file)
            print(f"{file} siap...")
    print("SEMUA SUARA SIAP")

generate_suara()

state = "INTRO"
intro_sudah_bicara = False
scan_mulai = None
scan_durasi = 30
fps_time = time.time()
menu_pilihan = ["VSCode", "Instagram", "YouTube"]
menu_index = 0
ily_tahap = 0
menu_cooldown = 0  # ← ganti time.sleep dengan cooldown!

def deteksi_jari(lm):
    jari = []
    if lm[4].x < lm[3].x:
        jari.append(True)
    else:
        jari.append(False)
    for ujung, pangkal in zip(ujung_jari, ujung_pangkal):
        if lm[ujung].y < lm[pangkal].y:
            jari.append(True)
        else:
            jari.append(False)
    return jari

def gambar_hati(frame, x, y, ukuran, warna):
    cv2.circle(frame, (x - ukuran//2, y), ukuran//2, warna, -1)
    cv2.circle(frame, (x + ukuran//2, y), ukuran//2, warna, -1)
    pts = np.array([(x - ukuran, y), (x + ukuran, y), (x, y + ukuran + 10)])
    cv2.fillPoly(frame, [pts], warna)

print("AI PERSONAL ASSISTANT LAUNCHER")
print("Initializing...")

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    sekarang = time.time()

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hasil = hands.process(frame_rgb)

    jari = []
    if hasil.multi_hand_landmarks:
        for hand_landmarks in hasil.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            jari = deteksi_jari(hand_landmarks.landmark)

    # STATE: INTRO
    if state == "INTRO":
        if not intro_sudah_bicara:
            speak("intro")
            intro_sudah_bicara = True

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, 150), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)

        cv2.putText(frame, "Selamat Datang, Tuan Muda Ashraf",
                   (10, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        cv2.putText(frame, "Tunjukkan Gesture Rahasia: I LOVE YOU",
                   (10, 90), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)

        warna_i    = (0, 255, 0) if ily_tahap >= 1 else (100, 100, 100)
        warna_love = (0, 255, 0) if ily_tahap >= 2 else (100, 100, 100)
        warna_you  = (0, 255, 0) if ily_tahap >= 3 else (100, 100, 100)

        cv2.putText(frame, "I",    (w//2 - 100, 140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, warna_i, 3)
        cv2.putText(frame, "LOVE", (w//2 - 40,  140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, warna_love, 3)
        cv2.putText(frame, "YOU",  (w//2 + 80,  140), cv2.FONT_HERSHEY_SIMPLEX, 1.5, warna_you, 3)

        if ily_tahap == 0:
            cv2.putText(frame, "Tunjuk: I (kelingking)", (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if jari == [False, False, False, False, True]:
                ily_tahap = 1

        elif ily_tahap == 1:
            cv2.putText(frame, "Tunjuk: LOVE (huruf L)", (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if jari == [True, True, False, False, False]:
                ily_tahap = 2

        elif ily_tahap == 2:
            cv2.putText(frame, "Tunjuk: YOU (I Love You)", (10, h-20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)
            if jari == [True, True, False, False, True]:
                ily_tahap = 3
                state = "SCANNING"
                speak("gesture_key")
                scan_mulai = sekarang

    # STATE: SCANNING
    elif state == "SCANNING":
        durasi = sekarang - scan_mulai
        persen = min(int((durasi / scan_durasi) * 100), 100)

        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 20), -1)
        cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

        scan_y = int((durasi % 2) / 2 * h)
        cv2.line(frame, (0, scan_y), (w, scan_y), (0, 255, 0), 2)

        bar_w = int(w * persen / 100)
        cv2.rectangle(frame, (0, h-30), (bar_w, h), (0, 255, 0), -1)
        cv2.putText(frame, f"SCANNING... {persen}%",
                   (10, h-35), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        cv2.putText(frame, "PALM BIOMETRIC SCAN",
                   (w//2 - 150, 50), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

        t = sekarang
        for i in range(5):
            x = int(w//2 + 200 * math.cos(t + i * 1.2))
            y = int(h//2 + 100 * math.sin(t * 0.5 + i))
            gambar_hati(frame, x, y, 15, (0, 0, 255))

        if persen >= 100:
            state = "MENU"
            speak("akses")

    # STATE: MENU
    elif state == "MENU":
        overlay = frame.copy()
        cv2.rectangle(overlay, (0, 0), (w, h), (0, 0, 0), -1)
        cv2.addWeighted(overlay, 0.7, frame, 0.3, 0, frame)

        cv2.putText(frame, "AKSES DITERIMA",
                   (w//2 - 150, 60), cv2.FONT_HERSHEY_SIMPLEX, 1.2, (0, 255, 0), 3)
        cv2.putText(frame, "Pilih Aplikasi:",
                   (10, 110), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 255), 2)

        for i, item in enumerate(menu_pilihan):
            warna = (0, 255, 255) if i == menu_index else (180, 180, 180)
            prefix = ">>> " if i == menu_index else "    "
            cv2.putText(frame, f"{prefix}{item}",
                       (50, 160 + i * 60), cv2.FONT_HERSHEY_SIMPLEX, 1, warna, 2)

        cv2.putText(frame, "Peace=Scroll  Jempol=Buka  Lima=Reset",
                   (10, h-20), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 0), 1)

        # Cooldown biar tidak lag
        if sekarang > menu_cooldown:
            if jari == [False, True, True, False, False]:  # Peace = scroll
                menu_index = (menu_index + 1) % len(menu_pilihan)
                menu_cooldown = sekarang + 0.8  # cooldown 0.8 detik

            elif jari == [True, False, False, False, False]:  # Jempol = buka
                pilihan = menu_pilihan[menu_index]
                if pilihan == "VSCode":
                    speak("vscode")
                    subprocess.Popen(["code"])
                elif pilihan == "Instagram":
                    speak("instagram")
                    subprocess.Popen(["xdg-open", "https://www.instagram.com/asepenterprise/"])
                elif pilihan == "YouTube":
                    speak("youtube")
                    subprocess.Popen(["xdg-open", "https://youtu.be/1WxooiESNoQ"])
                menu_cooldown = sekarang + 2

            elif jari == [True, True, True, True, True]:  # Lima = reset
                state = "INTRO"
                intro_sudah_bicara = False
                ily_tahap = 0

    fps = 1 / (time.time() - fps_time)
    fps_time = time.time()
    cv2.putText(frame, f"FPS:{int(fps)}", (w-80, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 0), 2)

    cv2.imshow('AI Personal Assistant', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()