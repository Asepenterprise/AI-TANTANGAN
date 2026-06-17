import cv2
import numpy as np

def nothing(x):
    pass

# Hubungkan ke DroidCam
cap = cv2.VideoCapture(0)

# Buat window untuk kalibrasi
cv2.namedWindow("Kalibrasi HSV")
cv2.resizeWindow("Kalibrasi HSV", 400, 250)

# Buat slider (Trackbar)
# Ingat: Di OpenCV, nilai Hue maksimal adalah 179. S dan V maksimal 255.
cv2.createTrackbar("H Min", "Kalibrasi HSV", 60, 179, nothing)
cv2.createTrackbar("S Min", "Kalibrasi HSV", 0, 255, nothing)
cv2.createTrackbar("V Min", "Kalibrasi HSV", 80, 255, nothing)

cv2.createTrackbar("H Max", "Kalibrasi HSV", 110, 179, nothing)
cv2.createTrackbar("S Max", "Kalibrasi HSV", 100, 255, nothing)
cv2.createTrackbar("V Max", "Kalibrasi HSV", 255, 255, nothing)

print("Geser slider sampai dinding berwarna PUTIH di window 'Mask', dan sisanya HITAM.")
print("Tekan 'q' untuk keluar.")

while True:
    ret, frame = cap.read()
    if not ret:
        break
        
    frame = cv2.flip(frame, 1)
    frame = cv2.resize(frame, (640, 480)) # Diperkecil agar ringan saat kalibrasi
    hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
    
    # Ambil nilai dari slider
    h_min = cv2.getTrackbarPos("H Min", "Kalibrasi HSV")
    s_min = cv2.getTrackbarPos("S Min", "Kalibrasi HSV")
    v_min = cv2.getTrackbarPos("V Min", "Kalibrasi HSV")
    h_max = cv2.getTrackbarPos("H Max", "Kalibrasi HSV")
    s_max = cv2.getTrackbarPos("S Max", "Kalibrasi HSV")
    v_max = cv2.getTrackbarPos("V Max", "Kalibrasi HSV")
    
    lower = np.array([h_min, s_min, v_min])
    upper = np.array([h_max, s_max, v_max])
    
    # Buat Masking
    mask = cv2.inRange(hsv, lower, upper)
    result = cv2.bitwise_and(frame, frame, mask=mask)
    
    # Tampilkan hasil
    cv2.imshow("1. Asli", frame)
    cv2.imshow("2. Mask (Fokus ke sini)", mask)
    cv2.imshow("3. Hasil Scan", result)
    
    if cv2.waitKey(1) & 0xFF == ord('q'):
        print("\n=== MASUKKAN NILAI INI KE DALAM GAME KAMU ===")
        print(f"lower_dinding = np.array([{h_min}, {s_min}, {v_min}])")
        print(f"upper_dinding = np.array([{h_max}, {s_max}, {v_max}])")
        break

cap.release()
cv2.destroyAllWindows()