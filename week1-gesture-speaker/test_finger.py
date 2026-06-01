import cv2
import mediapipe as mp

# BUKA KAMERA DULU
cap = cv2.VideoCapture(0)

# BARU inisialisasi MediaPipe
mp_hands = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hands = mp_hands.Hands(
    min_detection_confidence=0.7,
    min_tracking_confidence=0.7
)

Ujung_jari = [8, 12, 16, 20]
Pangkal_jari = [6, 10, 14, 18]

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
            if lm[4].x < lm[3].x:
                jari.append(True)
            else :
                jari.append(False)
                
            for ujung, pangkal in zip(Ujung_jari, Pangkal_jari):
                if lm[ujung].y < lm[pangkal].y:
                    jari.append(True)
                else:
                    jari.append(False)
            jumlah_jari = jari.count(True)
            cv2.putText(frame, f"Jari: {jumlah_jari}", (10, 50),
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)

    cv2.imshow('Finger Detection', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()