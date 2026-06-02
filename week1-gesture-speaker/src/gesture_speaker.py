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
    "Apa kabar?": "suara_apakabar.mp3"
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

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hasil = hands.process(frame_rgb)

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

            # GESTURE RECOGNITION
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
            if jari == [True, True, True, True, True]:
                gesture = "Lima"
            if jari == [False, True, False, False, True]:
                gesture = "Halo!"
            if jari == [True, False, False, False, False]:
                gesture = "Jempol!"
            if jari == [True, False, False, False, True]:
                gesture = "Apa kabar?"

            if gesture != "" and gesture != gesture_lama:
                speak(gesture)
                gesture_lama = gesture

            if gesture !="":
                cv2.putText(frame, f"Gesture: {gesture}", (10, 50),
                           cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)

    cv2.imshow('Gesture Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()