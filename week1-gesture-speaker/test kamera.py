import cv2
cap = cv2.VideoCapture(0)
if not cap.isOpened():
    print("GAGAL MENGAKSES KAMERA")
    cap.release()
    cv2.destroyAllWindows()
    raise SystemExit(1)
else:
    print("KAMERA BERHASIL DIBUKA")

while True:
    ret, frame = cap.read()
    if not ret:
        print("GAGAL MENGAMBIL FRAME")
        break

    cv2.imshow('test kamera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("GAGAL MENGAKSES PROGRAM")
        break

cap.release()
cv2.destroyAllWindows()