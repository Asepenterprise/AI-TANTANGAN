import cv2
import numpy as np
import time
import sqlite3 # Ditambahkan langsung untuk mempermudah query TRUNCATE/DELETE saat reset
from vision.detector import TargetDetector
from utils.database import GameDatabase

# === CONFIG MISI & WARNA (Dynamic) ===
misi_list = [
    {
        "id": 1,
        "judul": "ARTEFAK PERTAMA",
        "deskripsi": "Temukan dinding rahasia di rumahmu!",
        "petunjuk": "Arahkan kamera ke dinding yang tepat",
        "hsv_lower": [60, 0, 80],
        "hsv_upper": [110, 100, 255],
        "xp": 50,
        "hadiah_item": "Kunci Kuno Emas"
    },
    {
        "id": 2,
        "judul": "ARTEFAK KEDUA (RED CORE)",
        "deskripsi": "Cari energi merah di sekitarmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna merah terang",
        "hsv_lower": [0, 120, 70],
        "hsv_upper": [10, 255, 255],
        "xp": 100,
        "hadiah_item": "Kristal Merah Koron"
    },
    {
        "id": 3,
        "judul": "ARTEFAK KETIGA (BLUE MYSTIC)",
        "deskripsi": "Cari energi biru kuno di dekatmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna biru",
        "hsv_lower": [100, 150, 50],
        "hsv_upper": [140, 255, 255],
        "xp": 150,
        "hadiah_item": "Plakat Biru Atlantis"
    }
]

# === INITIALIZATION ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)

time.sleep(1)

if not cap.isOpened():
    print("Kamera gagal terhubung")
    exit()

detector = TargetDetector()

# === LOAD DATABASE PROGRESS ===
db = GameDatabase()
saved_xp, saved_level, saved_misi_index = db.load_game()

xp = saved_xp
level = saved_level
misi_index = saved_misi_index
daftar_inventory = db.ambil_all_inventory()

if misi_index >= len(misi_list):
    state = "GAME_OVER"
else:
    state = "INTRO"

story_index = 0
story_timer = time.time()
scan_progress = 0

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
# === KUMPULAN FUNGSI UI CORNER (DIFIX TOTAL BIAR RAPI) ===
# =========================================================

def teks_tengah(frame, teks, x_start, x_end, y, font, scale, warna, tebal):
    """Fungsi ajaib untuk membuat teks otomatis rata tengah (Centered) di OpenCV"""
    size = cv2.getTextSize(teks, font, scale, tebal)[0]
    lebar_teks = size[0]
    lebar_kotak = x_end - x_start
    x_terpusat = x_start + (lebar_kotak - lebar_teks) // 2
    cv2.putText(frame, teks, (x_terpusat, y), font, scale, warna, tebal)

def gambar_ui_header(frame, w, h):
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 15), -1)
    cv2.line(frame, (0, 60), (w, 60), (0, 255, 255), 2)
    
    cv2.putText(frame, "TREASURE HUNTER", (20, 40),
               cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 255), 2)
    
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (40, 40, 40), -1)
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (0, 255, 0), 1)
    cv2.putText(frame, f"XP: {xp} | LVL: {level}", (w-240, 36),
               cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

def gambar_ui_inventory(frame, w, h):
    """Memperlebar kotak tas agar muat banyak item dan rapi"""
    x1, y1, x2, y2 = 20, h-160, 650, h-80
    cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 20), -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
    
    cv2.putText(frame, "TAS INVENTORY:", (x1+15, y1+25), 
                cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
    
    teks_tas = ", ".join(daftar_inventory) if len(daftar_inventory) > 0 else "Kosong"
    cv2.putText(frame, teks_tas, (x1+15, y1+55), 
                cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

def gambar_hud_kamera(frame, w, h):
    warna_hud = (0, 200, 255)
    tebal = 3
    panjang = 40
    
    cv2.line(frame, (30, 80), (30+panjang, 80), warna_hud, tebal)
    cv2.line(frame, (30, 80), (30, 80+panjang), warna_hud, tebal)
    cv2.line(frame, (w-30, 80), (w-30-panjang, 80), warna_hud, tebal)
    cv2.line(frame, (w-30, 80), (w-30, 80+panjang), warna_hud, tebal)
    cv2.line(frame, (30, h-180), (30+panjang, h-180), warna_hud, tebal)
    cv2.line(frame, (30, h-180), (30, h-180-panjang), warna_hud, tebal)
    cv2.line(frame, (w-30, h-180), (w-30-panjang, h-180), warna_hud, tebal)
    cv2.line(frame, (w-30, h-180), (w-30, h-180-panjang), warna_hud, tebal)
    
    cx, cy = w//2, h//2
    cv2.circle(frame, (cx, cy), 5, (0, 255, 0), -1)
    cv2.circle(frame, (cx, cy), 20, (0, 255, 0), 1)

def teks_berkedip_tengah(frame, teks, x_start, x_end, y, font, scale, warna, tebal):
    if int(time.time() * 3) % 2 == 0:
        teks_tengah(frame, teks, x_start, x_end, y, font, scale, warna, tebal)

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
    gambar_ui_inventory(frame, w, h)

    # === STATE: INTRO ===
    if state == "INTRO":
        cv2.rectangle(frame, (50, 90), (w-50, h-190), (20, 20, 20), -1)
        cv2.rectangle(frame, (50, 90), (w-50, h-190), (0, 255, 255), 2)

        if story_index < len(story):
            for i, baris in enumerate(story[:story_index+1]):
                y = 130 + i * 28
                if y < h - 210:
                    cv2.putText(frame, baris, (80, y), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (220, 220, 220), 1)
            
            if sekarang - story_timer > 1:
                story_index += 1
                story_timer = sekarang
        else:
            teks_berkedip_tengah(frame, ">>> TEKAN SPASI UNTUK MULAI MISI <<<", 50, w-50, h-220, cv2.FONT_HERSHEY_SIMPLEX, 0.75, (0, 255, 0), 2)

    # === STATE: MISI ===
    elif state == "MISI":
        misi = misi_list[misi_index]
        gambar_hud_kamera(frame, w, h)

        cv2.rectangle(frame, (20, 80), (480, 200), (30, 30, 30), -1)
        cv2.rectangle(frame, (20, 80), (480, 200), (0, 200, 255), 2)

        cv2.putText(frame, f"{misi['judul']}", (35, 115), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1)
        cv2.putText(frame, misi['deskripsi'], (35, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Petunjuk: {misi['petunjuk']}", (35, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)

        persen = detector.hitung_persen_warna(frame, misi["hsv_lower"], misi["hsv_upper"])

        if persen > 8: 
            scan_progress = min(scan_progress + 2, 100)
        else:
            scan_progress = max(scan_progress - 1.5, 0)

        bar_color = (0, 0, 255) if scan_progress <= 40 else ((0, 255, 255) if scan_progress <= 80 else (0, 255, 0))
        bar_w = int((w-100) * scan_progress / 100)
        
        cv2.rectangle(frame, (50, h-60), (w-50, h-25), (50, 50, 50), -1)
        cv2.rectangle(frame, (50, h-60), (w-50, h-25), (200, 200, 200), 2)
        
        if scan_progress > 0:
            cv2.rectangle(frame, (50, h-60), (50+bar_w, h-25), bar_color, -1)
            
        teks_tengah(frame, f"MENGANALISA OBJEK... {int(scan_progress)}%", 50, w-50, h-37, 
                    cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0,0,0) if scan_progress > 50 else (255,255,255), 2)

        if scan_progress >= 100:
            state = "SUKSES"

    # === STATE: SUKSES ===
    elif state == "SUKSES":
        misi = misi_list[misi_index]
        x1, y1, x2, y2 = w//2-250, h//2-120, w//2+250, h//2+120
        cv2.rectangle(frame, (x1, y1), (x2, y2), (10, 40, 10), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 4)

        # Menggunakan kalkulasi teks_tengah agar simetris sempurna di dalam kotak pop-up
        teks_tengah(frame, "OBJEK TERIDENTIFIKASI!", x1, x2, y1+50, cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)
        teks_tengah(frame, f"REWARD: +{misi['xp']} XP", x1, x2, y1+110, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 255), 2)
        teks_berkedip_tengah(frame, ">>> TEKAN SPASI UNTUK LANJUT <<<", x1, x2, y1+180, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 255, 255), 2)

    # === STATE: GAME OVER ===
    elif state == "GAME_OVER":
        x1, y1, x2, y2 = w//2-300, h//2-140, w//2+300, h//2+140
        cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 40), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 215, 0), 3)
        
        # Centering teks tamat
        teks_tengah(frame, "ALL MISI COMPLETED!", x1, x2, y1+50, cv2.FONT_HERSHEY_DUPLEX, 1.0, (255, 215, 0), 2)
        teks_tengah(frame, f"TOTAL XP AKHIR: {xp}", x1, x2, y1+110, cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)
        teks_tengah(frame, "YEYY KAMU BERHASIL!!!", x1, x2, y1+160, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)
        
        # PETUNJUK TOMBOL RESET BARU!
        teks_berkedip_tengah(frame, ">>> TEKAN 'R' UNTUK MENGULANG GAME <<<", x1, x2, y1+220, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)

    cv2.imshow('Treasure Hunter - Asep enterprise', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    
    # === FITUR RESET GAME (DITEKAN SAAT SCREEN GAME OVER) ===
    elif key == ord('r') or key == ord('R'):
        if state == "GAME_OVER":
            # 1. Kosongkan isi tabel inventory & kembalikan player progress ke awal di DB
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM inventory')
            conn.commit()
            conn.close()
            
            db.save_game(0, 1, 0) # XP=0, LVL=1, misi_index=0
            
            # 2. Reset status variable game lokal
            xp, level, misi_index = 0, 1, 0
            daftar_inventory = []
            scan_progress = 0
            story_index = 0
            story_timer = time.time()
            state = "INTRO"
            print("[DB] Game berhasil di-reset ke nol!")

    elif key == ord(' '):  # SPASI
        if state == "INTRO" and story_index >= len(story):
            state = "MISI"
            scan_progress = 0
        elif state == "SUKSES":
            misi_sekarang = misi_list[misi_index]
            xp += misi_sekarang['xp']
            level = 1 + (xp // 100)
            
            db.tambah_ke_inventory(misi_sekarang['hadiah_item'], f"Didapat dari {misi_sekarang['judul']}")
            db.save_game(xp, level, misi_index + 1)
            daftar_inventory = db.ambil_all_inventory()
            
            misi_index += 1
            scan_progress = 0
            if misi_index >= len(misi_list):
                state = "GAME_OVER"
            else:
                state = "MISI"

cap.release()
cv2.destroyAllWindows()