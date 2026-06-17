import cv2
import numpy as np
import time
import math

cap = cv2.VideoCapture(0)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

time.sleep(2)

if not cap.isOpened():
    print("Kamera gagal terhubung")
    exit()

# === WARNA DINDING (HSV dari Kalibrasimu) ===
lower_dinding = np.array([60, 0, 80])
upper_dinding = np.array([110, 100, 255])

# === STORY ===
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

# === MISI ===
misi_list = [
    {
        "id": 1,
        "judul": "ARTEFAK PERTAMA",
        "deskripsi": "Temukan dinding rahasia di rumahmu!",
        "petunjuk": "Arahkan kamera ke dinding yang tepat",
        "xp": 50
    },
    {
        "id": 2,
        "judul": "ARTEFAK KEDUA",
        "deskripsi": "Misi 2 coming soon...",
        "petunjuk": "Coming soon",
        "xp": 100
    },
    {
        "id": 3,
        "judul": "ARTEFAK KETIGA",
        "deskripsi": "Misi 3 coming soon...",
        "petunjuk": "Coming soon",
        "xp": 150
    }
]

# === STATE GAME ===
state = "INTRO"
story_index = 0
story_timer = time.time()
misi_index = 0
xp = 0
level = 1
scan_progress = 0

# =========================================================
# === KUMPULAN FUNGSI UI & UX BARU (LEBIH RAME) ===
# =========================================================

def gambar_ui_header(frame, w, h):
    # Base header
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 15), -1)
    cv2.line(frame, (0, 60), (w, 60), (0, 255, 255), 2) # Garis neon bawah header
    
    # Judul Game
    cv2.putText(frame, "TREASURE HUNTER AI", (20, 40),
               cv2.FONT_HERSHEY_DUPLEX, 1, (0, 255, 255), 2)
    
    # Status Player
    cv2.rectangle(frame, (w-250, 15), (w-20, 45), (40, 40, 40), -1)
    cv2.rectangle(frame, (w-250, 15), (w-20, 45), (0, 255, 0), 1)
    cv2.putText(frame, f"XP: {xp} | LVL: {level}", (w-230, 35),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)

def gambar_hud_kamera(frame, w, h):
    """Memberikan efek AR/Kamera Sci-Fi"""
    warna_hud = (0, 200, 255) # Cyan terang
    tebal = 3
    panjang = 40
    
    # Sudut Kiri Atas
    cv2.line(frame, (30, 80), (30+panjang, 80), warna_hud, tebal)
    cv2.line(frame, (30, 80), (30, 80+panjang), warna_hud, tebal)
    # Sudut Kanan Atas
    cv2.line(frame, (w-30, 80), (w-30-panjang, 80), warna_hud, tebal)
    cv2.line(frame, (w-30, 80), (w-30, 80+panjang), warna_hud, tebal)
    # Sudut Kiri Bawah
    cv2.line(frame, (30, h-30), (30+panjang, h-30), warna_hud, tebal)
    cv2.line(frame, (30, h-30), (30, h-30-panjang), warna_hud, tebal)
    # Sudut Kanan Bawah
    cv2.line(frame, (w-30, h-30), (w-30-panjang, h-30), warna_hud, tebal)
    cv2.line(frame, (w-30, h-30), (w-30, h-30-panjang), warna_hud, tebal)
    
    # Crosshair Tengah
    cx, cy = w//2, h//2
    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    cv2.circle(frame, (cx, cy), 20, (0, 255, 0), 1)
    cv2.line(frame, (cx-30, cy), (cx-10, cy), (0, 255, 0), 2)
    cv2.line(frame, (cx+10, cy), (cx+30, cy), (0, 255, 0), 2)
    cv2.line(frame, (cx, cy-30), (cx, cy-10), (0, 255, 0), 2)
    cv2.line(frame, (cx, cy+10), (cx, cy+30), (0, 255, 0), 2)

def teks_berkedip(frame, teks, x, y, font, scale, warna, tebal):
    """Fungsi untuk membuat teks kelap-kelip"""
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

    # Overlay gelap (Background environment)
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (10, 10, 20), -1) # Agak kebiruan gelap
    cv2.addWeighted(overlay, 0.4, frame, 0.6, 0, frame)

    # Selalu munculkan Header UI
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
            
            if sekarang - story_timer > 1: # Ganti angka 1 untuk percepat/perlambat teks
                story_index += 1
                story_timer = sekarang
        else:
            teks_berkedip(frame, ">>> TEKAN SPASI UNTUK MULAI MISI <<<", 
                         w//2-250, h-80, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    # === STATE: MISI ===
    elif state == "MISI":
        misi = misi_list[misi_index]
        
        # Tampilkan efek kamera AR
        gambar_hud_kamera(frame, w, h)

        # Panel info misi (Lebih modern)
        cv2.rectangle(frame, (20, 80), (450, 200), (30, 30, 30), -1)
        cv2.rectangle(frame, (20, 80), (450, 200), (0, 200, 255), 2)

        cv2.putText(frame, f"TARGET: {misi['judul']}", (35, 115), 
                    cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 255), 1)
        cv2.putText(frame, misi['deskripsi'], (35, 145), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)
        cv2.putText(frame, f"Petunjuk: {misi['petunjuk']}", (35, 180), 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)

        # Deteksi dinding (Logika inti tidak diubah)
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        mask = cv2.inRange(hsv, lower_dinding, upper_dinding)
        total_pixel = h * w
        pixel_dinding = cv2.countNonZero(mask)
        persen = (pixel_dinding / total_pixel) * 100

        # Progress Update
        if persen > 10: # Dibuat sedikit lebih sensitif (10%)
            scan_progress = min(scan_progress + 2, 100)
        else:
            scan_progress = max(scan_progress - 1.5, 0) # Penurunan sedikit lebih lambat biar ga bikin emosi

        # Dynamic Progress Bar (Berubah warna tergantung progress)
        bar_color = (0, 0, 255) # Merah default
        if scan_progress > 40:
            bar_color = (0, 255, 255) # Kuning
        if scan_progress > 80:
            bar_color = (0, 255, 0) # Hijau
            
        bar_w = int((w-100) * scan_progress / 100)
        
        # Background bar
        cv2.rectangle(frame, (50, h-70), (w-50, h-30), (50, 50, 50), -1)
        cv2.rectangle(frame, (50, h-70), (w-50, h-30), (200, 200, 200), 2)
        
        # Isi bar
        if scan_progress > 0:
            cv2.rectangle(frame, (50, h-70), (50+bar_w, h-30), bar_color, -1)
            
        # Teks progress
        cv2.putText(frame, f"MENGANALISA OBJEK... {int(scan_progress)}%", 
                   (w//2-150, h-42), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0,0,0) if scan_progress > 50 else (255,255,255), 2)

        if scan_progress >= 100:
            state = "SUKSES"

    # === STATE: SUKSES ===
    elif state == "SUKSES":
        misi = misi_list[misi_index]

        # Efek kotak sukses yang mencolok
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
        cv2.rectangle(frame, (w//2-300, h//2-120), (w//2+300, h//2+120), (255, 215, 0), 3) # Border emas
        
        cv2.putText(frame, "MISI SELESAI!", (w//2-130, h//2-50),
                   cv2.FONT_HERSHEY_DUPLEX, 1.2, (255, 215, 0), 2)
        cv2.putText(frame, f"TOTAL XP AKHIR: {xp}", (w//2-150, h//2+10),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
        cv2.putText(frame, "Impian Ash terwujud. Kerja bagus, Hunter!", (w//2-230, h//2+60),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.7, (200, 200, 200), 1)

    # Tampilkan Render Frame
    cv2.imshow('Treasure Hunter AI HUD', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    elif key == ord(' '):  # SPASI
        if state == "INTRO" and story_index >= len(story):
            state = "MISI"
            scan_progress = 0
        elif state == "SUKSES":
            xp += misi_list[misi_index]['xp']
            misi_index += 1
            scan_progress = 0
            if misi_index >= len(misi_list):
                state = "GAME_OVER"
            else:
                state = "MISI"

cap.release()
cv2.destroyAllWindows()