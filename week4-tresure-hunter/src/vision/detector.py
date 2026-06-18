import cv2
import numpy as np

class TargetDetector:
    def __init__(self):
        pass

    def hitung_persen_warna(self, frame, lower_hsv, upper_hsv):
        """Menghitung berapa persen warna target yang ada di layar"""
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, np.array(lower_hsv), np.array(upper_hsv))
        
        # Opsional: Bersihkan noise gambarnya sedikit (Morphology)
        mask = cv2.erode(mask, None, iterations=2)
        mask = cv2.dilate(mask, None, iterations=2)
        
        total_pixel = frame.shape[0] * frame.shape[1]
        pixel_target = cv2.countNonZero(mask)
        return (pixel_target / total_pixel) * 100