import cv2
import numpy as np

class TargetDetector:
    def __init__(self):
        pass

    def hitung_persen_warna(self, frame, hsv_lower, hsv_upper):
        """Menghitung persentase kehadiran warna target di dalam frame kamera"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        
        lower = np.array(hsv_lower, dtype="uint8")
        upper = np.array(hsv_upper, dtype="uint8")
        
        mask = cv2.inRange(hsv, lower, upper)
        
        # Hitung luas piksel warna target berbanding ukuran frame total
        total_piksel = mask.size
        piksel_cocok = np.sum(mask == 255)
        
        persentase = (piksel_cocok / total_piksel) * 100
        return persentase