import cv2
import numpy as np
import time
from vision.detector import TargetDetector

# === CONFIG MISI & WARNA (Dynamic) ===
# Sekarang rentang warna diatur per misi!
misi_list = [
    {
        "id": 1,
        "judul": "ARTEFAK PERTAMA",
        "deskripsi": "Temukan dinding rahasia di rumahmu!",
        "petunjuk": "Arahkan kamera ke dinding yang tepat",
        "hsv_lower": [60, 0, 80],
        "hsv_upper": [110, 100, 255],
        "xp": 50
    },
    {
        "id": 2,
        "judul": "ARTEFAK KEDUA (RED CORE)",
        "deskripsi": "Cari energi merah di sekitarmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna merah terang",
        "hsv_lower": [0, 120, 70],
        "hsv_upper": [10, 255, 255],
        "xp": 100
    },
    {
        "id": 3,
        "judul": "ARTEFAK KETIGA (BLUE MYSTIC)",
        "deskripsi": "Cari energi biru kuno di dekatmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna biru",
        "hsv_lower": [100, 150, 50],
        "hsv_upper": [140, 255, 255],
        "xp": 150
    }
]

# === INITIALIZATION ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

time.sleep(2)

if not cap.isOpened():
    print("Kamera gagal terhubung")
    exit()

# Panggil class detector dari file luar
detector = TargetDetector()

# === STATE GAME ===
state = "INTRO"
story_index = 0
story_timer = time.time()
misi_index = 0
xp = 0
level = 1
scan_progress = 0

# === COPIED STORY FROM DAY 1 ===
story = [
    "Dahulu kala ada seorang anak bernama Ash...",
    "Dia bercita-cita menjadi developer terkenal.",
    "Ingin menggendong ekonomi keluarganya.",
    "Dia selalu kalah dalam segala hal,",
    "bahkan soal percintaan.",
    "Tapi dia tidak menyerah.",
    "",
    "Suatu hari, Ash menemukan peta kuno...",
    "3 artefak legendaris tersembunyi di rumahnya!",
    "",
    "Siapapun yang mengumpulkan ketiganya",
    "akan mewujudkan semua impiannya.",
    "",
    'Ash berkata: "Ini kesempatanku!"',
    "",
    "Selamat datang di dunia nyata, ASH.",
    "Misi dimulai..."
]

# =========================================================
# === KUMPULAN FUNGSI UI & UX BARU (LEBIH RAME) ===
# =========================================================

def gambar_ui_header(frame, w, h):
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 15), -1)
    cv2.line(frame, (0, 60), (w, 60), (0, 255, 255), 2)
    
    cv2.putText(frame, "TREASURE HUNTER AI", (20, 40),
               cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2)
    
    cv2.rectangle(frame, (w-250, 15), (w-20, 45), (40, 40, 40), -1)
    cv2.rectangle(frame, (w-250, 15), (w-20, 45), (0, 255, 0), 1)
    cv2.putText(frame, f"XP: {xp} | LVL: {level}", (w-230, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def gambar_hud_kamera(frame, w, h):
    warna_hud = (0, 200, 255)
    tebal = 3
    panjang = 40
    
    cv2.line(frame, (30, 80), (30+panjang, 80), warna_hud, tebal)
    cv2.line(frame, (30, 80), (30, 80+panjang), warna_hud, tebal)
    cv2.line(frame, (w-30, 80), (w-30-panjang, 80), warna_hud, tebal)
    cv2.line(frame, (w-30, 80), (w-30, 80+panjang), warna_hud, tebal)
    cv2.line(frame, (30, h-30), (30+panjang, h-30), warna_hud, tebal)
    cv2.line(frame, (30, h-30), (30, h-30-panjang), warna_hud, tebal)
    cv2.line(frame, (w-30, h-30), (w-30-panjang, h-30), warna_hud, tebal)
    cv2.line(frame, (w-30, h-30), (w-30, h-30-panjang), warna_hud, tebal)
    
    cx, cy = w//2, h//2
    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    cv2.circle(frame, (cx, cy), 20, (0, 255, 0), 1)
    cv2.line(frame, (cx-30, cy), (cx-10, cy), (0, 255, 0), 2)
    cv2.line(frame, (cx+10, cy), (cx+30, cy), (0, 255, 0), 2)
    cv2.line(frame, (cx, cy-30), (cx, cy-10), (0, 255, 0), 2)
    cv2.line(frame, (cx, cy+10), (cx, cy+30), (0, 255, 0), 2)

def teks_berkedip(frame, teks, x, y, font, scale, warna, tebal):
    if int(time.time() * 3) % 2 == 0:
        cv2.putText(frame, teks, (x, y), font, scale, warna, tebal)

# =========================================================
# === MAIN LOOP UTAMA ===
# =========================================================

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    sekarang = time.time()

    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (10, 10, 20), -1)
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    gambar_ui_header(frame, w, h)

    # === STATE: INTRO ===
    if state == "INTRO":
        cv2.rectangle(frame, (50, 90), (w-50, h-50), (20, 20, 20), -1)
        cv2.rectangle(frame, (50, 90), (w-50, h-50), (0, 255, 255), 2)

        if story_index < len(story):
            for i, baris in enumerate(story[:story_index+1]):
                y = 140 + i * 30
                if y < h - 80:
                    cv2.putText(frame, baris, (80, y),
                               cv2.FONT_HERSHEY_SIMPLEX, 0.6, (220, 220, 220), 1)
            
            if sekarang - story_timer > 1:
                story_index += 1
                story_timer = sekarang
        else:
            teks_berkedip(frame, ">>> TEKAN SPASI UNTUK MULAI MISI <<<", 
                         w//2-250, h-80, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # === STATE: MISI ===
    elif state == "MISI":
        misi = misi_list[misi_index]
        gambar_hud_kamera(frame, w, h)

        # Panel info misi
        cv2.rectangle(frame, (20, 80), (450, 200), (30, 30, 30), -1)
        cv2.rectangle(frame, (20, 80), (450, 200), (0, 200, 255), 2)

        cv2.putText(frame, f"TARGET: {misi['judul']}", (35, 115), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 1)
        cv2.putText(frame, misi['deskripsi'], (35, 145), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(frame, f"Petunjuk: {misi['petunjuk']}", (35, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # FITUR BARU DAY 2: Panggil modul detector luar dengan parameter dinamis!
        persen = detector.hitung_persen_warna(frame, misi["hsv_lower"], misi["hsv_upper"])

        # Progress Update
        if persen > 8: 
            scan_progress = min(scan_progress + 2, 100)
        else:
            scan_progress = max(scan_progress - 1.5, 0)

        # Dynamic Progress Bar
        bar_color = (0, 0, 255)
        if scan_progress > 40:
            bar_color = (0, 255, 255)
        if scan_progress > 80:
            bar_color = (0, 255, 0)
            
        bar_w = int((w-100) * scan_progress / 100)
        
        cv2.rectangle(frame, (50, h-70), (w-50, h-30), (50, 50, 50), -1)
        cv2.rectangle(frame, (50, h-70), (w-50, h-30), (200, 200, 200), 2)
        
        if scan_progress > 0:
            cv2.rectangle(frame, (50, h-70), (50+bar_w, h-30), bar_color, -1)
            
        cv2.putText(frame, f"MENGANALISA OBJEK... {int(scan_progress)}%", 
                   (w//2-150, h-42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0) if scan_progress > 50 else (255,255,255), 2)

        if scan_progress >= 100:
            state = "SUKSES"

    # === STATE: SUKSES ===
    elif state == "SUKSES":
        misi = misi_list[misi_index]

        cv2.rectangle(frame, (w//2-250, h//2-100), (w//2+250, h//2+120), (10, 40, 10), -1)
        cv2.rectangle(frame, (w//2-250, h//2-100), (w//2+250, h//2+120), (0, 255, 0), 4)

        cv2.putText(frame, "OBJEK TERIDENTIFIKASI!", (w//2-210, h//2-40),
                   cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, f"REWARD: +{misi['xp']} XP", (w//2-120, h//2+20),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
        
        teks_berkedip(frame, ">>> TEKAN SPASI UNTUK LANJUT <<<", 
                     w//2-190, h//2+80, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (255, 255, 255), 2)

    # === STATE: GAME OVER ===
    elif state == "GAME_OVER":
        cv2.rectangle(frame, (w//2-300, h//2-120), (w//2+300, h//2+120), (20, 20, 40), -1)
        cv2.rectangle(frame, (w//2-300, h//2-120), (w//2+300, h//2+120), (255, 215, 0), 3)
        
        cv2.putText(frame, "ALL MISI COMPLETED!", (w//2-180, h//2-50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 215, 0), 2)
        cv2.putText(frame, f"TOTAL XP AKHIR: {xp}", (w//2-150, h//2+10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Ekonomi keluarga berhasil digendong Ash!", (w//2-260, h//2+60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

    cv2.imshow('Treasure Hunter AI HUD', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord(' '):  # SPASI
        if state == "INTRO" and story_index >= len(story):
            state = "MISI"
            scan_progress = 0
        elif state == "SUKSES":
            # UPDATE REWARD & AUTO LEVEL UP FORMULA
            xp += misi_list[misi_index]['xp']
            level = 1 + (xp // 100) # Tiap kelipatan 100 XP, level naik!
            
            misi_index += 1
            scan_progress = 0
            if misi_index >= len(misi_list):
                state = "GAME_OVER"
            else:
                state = "MISI"

cap.release()
cv2.destroyAllWindows()