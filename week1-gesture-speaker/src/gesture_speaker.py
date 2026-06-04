import subprocess

import time
import threading

from gtts import  gTTS
import os
import pygame

import cv2
import mediapipe as mp

cap = cv2.VideoCapture(0)

mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils
hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

Ujung_jari = [8, 12, 16, 20]
Pangkal_jari = [6, 10, 14, 18]

#GTTS
def speak(text):
    def play():
        try:
            if pygame.mixer.music.get_busy():
                return
            file = suara_list.get(text)
            if file and os.path.exists(file):
                pygame.mixer.music.load(file)
                pygame.mixer.music.play()
        except:
            print(f"Gagal bicara: {text}")
    
    threading.Thread(target=play).start()

suara_list = {
    "Nol": "suara_nol.mp3",
    "Satu": "suara_satu.mp3",
    "Dua": "suara_dua.mp3",
    "Tiga": "suara_tiga.mp3",
    "Empat": "suara_empat.mp3",
    "Lima": "suara_lima.mp3",
    "Halo!": "suara_halo.mp3",
    "Jempol!": "suara_jempol.mp3",
    "Apa kabar?": "suara_apakabar.mp3",
    "Aku Ashraf": "suara_akuashraf.mp3",
    "I": "suara_i.mp3",
    "LOVE": "suara_Love.mp3",
    "YOU": "suara_you.mp3"
}

print("generating suara...")
for gesture, file in suara_list.items():
 if not os.path.exists(file):
     tts = gTTS(text=gesture, lang='id')
     tts.save(file)
     print(f"selesai {file} sudah siap")

pygame.mixer.init()
print("Suara siap")
gesture_lama = ""

fps_time = time.time()

scan_status = "SIAP"
scan_status = "SCANNING"
scan_status = "AKSES DITERIMA"
scan_selesai = "COOLDOWN"

def tampilkan_ui(frame, gesture, fps, gesture_hold = "", waktu_mulai = None):
    h, w, _ = frame.shape

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, 60), (0, 0, 0), -1)
    cv2.addWeighted(overlay, 0.5, frame, 0.5, 0, frame)

    cv2.putText(frame, f'FPS: {int(fps)}', (10, 30), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 0), 2)
    
    if gesture != "":
        cv2.putText(frame, f"Gesture: {gesture}", (10, 80),
                 cv2.FONT_HERSHEY_SIMPLEX, 1.5, (0, 255, 255), 3)
        #BIOMETRIC
        if gesture_hold != "" and waktu_mulai is not None:
            durasi = time.time() - waktu_mulai
            persen = max(0, min(int((durasi / 3) * 100), 100))
            bar_width = int((w * persen) / 100)
            cv2.rectangle(frame, (0, h-20), (bar_width, h), (0, 255, 0), -1)
            cv2.putText(frame, f"{scan_status} {persen}%",(10, h - 50), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
                    

gesture_lama = ""
tahap = 0
mode = "normal"
fps_time = time.time()
waktu_mulai = None
gesture_hold = ""
scan_selesai = False
cooldown = 0

print("gesture=",gesture)
print("hold=", gesture_hold)


def buka_app(gesture):
    print("MEMBUKA:", gesture)

    try:
        if gesture == "Peace":
            subprocess.Popen(["code"])

        elif gesture == "Jempol":
            subprocess.Popen([
                "xdg-open",
                "https://www.instagram.com/asepenterprise/"
            ])

        elif gesture == "Telapak":
            subprocess.Popen([
                "xdg-open",
                "https://youtu.be/1WxooiESNoQ?si=RVG0ws-9AFN72S6d"
            ])

    except Exception as e:
        print("ERROR:", e)

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue
    frame = cv2.flip(frame, 1)

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hasil = hands.process(frame_rgb)

    gesture = ""
    if hasil.multi_hand_landmarks:
        for hand_landmarks in hasil.multi_hand_landmarks:
            mp_draw.draw_landmarks(frame, hand_landmarks, mp_hands.HAND_CONNECTIONS)
            lm = hand_landmarks.landmark
            jari = []

            # IBU JARI
            if lm[4].x < lm[3].x:
                jari.append(True)
            else:
                jari.append(False)

            # 4 JARI LAINNYA
            for ujung, pangkal in zip(Ujung_jari, Pangkal_jari):
                if lm[ujung].y < lm[pangkal].y:
                    jari.append(True)
                else:
                    jari.append(False)

                gesture = ""
            if jari == [False, False, False, False, False]:
               gesture = "Nol"
            if jari == [False, True, False, False, False]:
               gesture = "Satu"
            if jari == [False, True, True, False, False]:
               gesture = "Dua"
            if jari == [False, True, True, True, False]:
               gesture = "Tiga"
            if jari == [False, True, True, True, True]:
               gesture = "Empat"

            # BIOMETRIC GESTURES
            if jari == [False, True, True, False, False]:
               gesture = "Peace"
            if jari == [True, False, False, False, False]:
               gesture = "Jempol"
            if jari == [True, True, True, True, True]:
               gesture = "Telapak"

            # 
            if gesture in ["Peace", "Jempol", "Telapak"]:
              
              sekarang = time.time()

              if sekarang < cooldown:
                 scan_status = "COOLDOWN"

              else:
                 
              
                if gesture_hold == "":
                   gesture_hold = gesture
                   waktu_mulai = sekarang
                   scan_selesai = False

                   scan_status = "SCANNING"

    # gesture masih sama
                elif gesture == gesture_hold and not scan_selesai:
                   durasi = sekarang - waktu_mulai
                   print(
                         "gesture =", gesture,
                         "hold =", gesture_hold,
                         "durasi =", round(durasi,2)
                          )

                   if durasi >= 3:
                      scan_status = "AKSES DITERIMA"
                      print("SCAN : BERHASIL", gesture)

                   buka_app(gesture)

                   scan_selesai = True

                   cooldown = sekarang + 5

                   gesture_hold = ""
                   waktu_mulai = None


                elif gesture != gesture_hold:
                   
                    if gesture in ["Peace", "Jempol", "Telapak"]:
                   
                        gesture_hold = gesture
                        waktu_mulai = sekarang
                        scan_selesai = False

   
            else:
                gesture_hold = ""
                waktu_mulai = None 
                scan_selesai = False

                scan_status = "SCAN SIAP"
 
       
    if gesture != "" and gesture != gesture_lama:
       speak(gesture)
       gesture_lama = gesture

    fps = 1 / (time.time() - fps_time)
    fps_time = time.time()
    tampilkan_ui(frame, gesture, fps, gesture_hold, waktu_mulai)

    cv2.imshow('Gesture Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()