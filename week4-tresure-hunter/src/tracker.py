import cv2
import numpy as np

def nothing(x):
    pass

# 1. Inisialisasi Kamera
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

# 2. Bikin Window Control buat Trackbar Slider
cv2.namedWindow("Cyberpunk Control Panel")
cv2.resizeWindow("Cyberpunk Control Panel", 400, 350)

# 3. Buat Slider untuk Lower dan Upper HSV
cv2.createTrackbar("Lower - H", "Cyberpunk Control Panel", 0, 180, nothing)
cv2.createTrackbar("Lower - S", "Cyberpunk Control Panel", 0, 255, nothing)
cv2.createTrackbar("Lower - V", "Cyberpunk Control Panel", 0, 255, nothing)

cv2.createTrackbar("Upper - H", "Cyberpunk Control Panel", 180, 180, nothing)
cv2.createTrackbar("Upper - S", "Cyberpunk Control Panel", 255, 255, nothing)
cv2.createTrackbar("Upper - V", "Cyberpunk Control Panel", 255, 255, nothing)

print("[INFO] Tracker Aktif! Geser slider sampai objek lu berwarna PUTIH di jendela MASK.")
print("[INFO] Tekan 'Q' untuk keluar dan menyalin data HSV.")

while True:
    ret, frame = cap.read()
    if not ret or frame is None: break
    
    frame = cv2.flip(frame, 1)
    # Konversi BGR asli ke HSV
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # 4. Ambil Posisi Slider secara Real-Time
    lh = cv2.getTrackbarPos("Lower - H", "Cyberpunk Control Panel")
    ls = cv2.getTrackbarPos("Lower - S", "Cyberpunk Control Panel")
    lv = cv2.getTrackbarPos("Lower - V", "Cyberpunk Control Panel")
    
    uh = cv2.getTrackbarPos("Upper - H", "Cyberpunk Control Panel")
    us = cv2.getTrackbarPos("Upper - S", "Cyberpunk Control Panel")
    uv = cv2.getTrackbarPos("Upper - V", "Cyberpunk Control Panel")
    
    # Satukan nilai ke matriks NumPy
    lower_bound = np.array([lh, ls, lv])
    upper_bound = np.array([uh, us, uv])
    
    # 5. Filter Warna Menggunakan Masking
    mask = cv2.inRange(hsv, lower_bound, upper_bound)
    
    # Potong frame asli agar hanya memunculkan warna yang terfilter (Opsional/Biar Keren)
    hasil_filter = cv2.bitwise_and(frame, frame, mask=mask)
    
    # 6. Tampilkan Semua Window
    cv2.imshow("Kamera Asli", frame)
    cv2.imshow("Jendela Mask (Target Putih)", mask)
    cv2.imshow("Hasil Filter Objek", hasil_filter)
    
    # Tekan 'q' buat stop dan ngeprint angkanya di terminal
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n" + "="*40)
        print(" HASIL KALIBRASI WARNA COCOK DI KAMAR LU:")
        print(f" 'hsv_lower': [{lh}, {ls}, {lv}]")
        print(f" 'hsv_upper': [{uh}, {us}, {uv}]")
        print("="*40)
        break

cap.release()
cv2.destroyAllWindows()