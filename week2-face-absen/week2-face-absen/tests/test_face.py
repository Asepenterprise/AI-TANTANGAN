

import cv2
import face_recognition

# Buka kamera
cap = cv2.VideoCapture(0)

while True:
    ret, frame = cap.read()
    if not ret:
        continue
        
    rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)

    kecil = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
    rgb = cv2.cvtColor(kecil, cv2.COLOR_BGR2RGB )
    lokasi_wajah = face_recognition.face_locations(rgb)
    lokasi_wajah = [(t*4, r*4, b*4, l*4) for t,r,b,l in lokasi_wajah]

    for top, right, bottom, left in lokasi_wajah:
        cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
        cv2.putText(frame, "Ashraf ganteng", (left, top-10),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)

    cv2.imshow('Face Detection', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()
