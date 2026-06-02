#LIBRARY

import cv2
import mediapipe as mp

#INITIAL MEDIAPIPE
mp_hand = mp.solutions.hands
mp_draw = mp.solutions.drawing_utils

hand = mp_hand.Hands(
    min_detection_confidence= 0.7,
    min_tracking_confidence= 0.7
)

cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        break

    frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
    hasil = hand.process(frame_rgb)

    if hasil.multi_hand_landmarks:
      for hand_landmark in hasil.multi_hand_landmarks:
        mp_draw.draw_landmarks(frame, hand_landmark, mp_hand.HAND_CONNECTIONS)

    cv2.imshow('test mediapipe', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
       break

cap.release()
cv2.destroyAllWindows()