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

    org = (10, 30)
    fontFace = cv2.FONT_HERSHEY_SIMPLEX
    fontScale = 1
    color = (0, 255, 0)
    thickness = 2
    cv2.putText(frame, "KAMERA AKTIF", org, fontFace, fontScale, color, thickness)

    lebar = cap.get(cv2.CAP_PROP_FRAME_WIDTH)
    tinggi = cap.get(cv2.CAP_PROP_FRAME_HEIGHT)

    teks = f"Resolusi: {int(lebar)}x{int(tinggi)}"
    cv2.putText(frame, teks, (10, int(tinggi) - 20), fontFace, 0.7, (255, 255, 0), 2)

    cv2.imshow('test kamera', frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("PROGRAM DITUTUP")
        break

cap.release()
cv2.destroyAllWindows()