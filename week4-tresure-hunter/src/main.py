import cv2
import numpy as np
import time
import sqlite3 
from vision.detector import TargetDetector
from utils.database import GameDatabase
from utils.audio import GameAudio 

# === CONFIG MISI & WARNA (Dynamic dengan batasan WAKTU) ===
misi_list = [
    {
        "id": 1,
        "judul": "ARTEFAK PERTAMA",
        "deskripsi": "Temukan dinding rahasia di rumahmu!",
        "petunjuk": "Arahkan kamera ke dinding yang tepat",
        "hsv_lower": [60, 0, 80],
        "hsv_upper": [110, 100, 255],
        "xp": 50,
        "hadiah_item": "Kunci Kuno Emas",
        "durasi": 20  # Batas waktu per misi (detik)
    },
    {
        "id": 2,
        "judul": "ARTEFAK KEDUA (RED CORE)",
        "deskripsi": "Cari energi merah di sekitarmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna merah terang",
        "hsv_lower": [0, 120, 70],
        "hsv_upper": [10, 255, 255],
        "xp": 100,
        "hadiah_item": "Kristal Merah Koron",
        "durasi": 15
    },
    {
        "id": 3,
        "judul": "ARTEFAK KETIGA (BLUE MYSTIC)",
        "deskripsi": "Cari energi biru kuno di dekatmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna biru",
        "hsv_lower": [100, 150, 50],
        "hsv_upper": [140, 255, 255],
        "xp": 150,
        "hadiah_item": "Plakat Biru Atlantis",
        "durasi": 15
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
db = GameDatabase()
audio = GameAudio() 

# Load progress lama dari SQLite
saved_xp, saved_level, saved_misi_index = db.load_game()

xp = saved_xp
level = saved_level
misi_index = saved_misi_index
daftar_inventory = db.ambil_all_inventory()

# Manajemen Variabel Global & Leaderboard Speedrun
game_start_time = 0
total_waktu_bermain = 0
skor_tercatat = False
top_skor_list = []

if misi_index >= len(misi_list):
    state = "GAME_OVER"
    top_skor_list = db.ambil_top_skor(3) # Load leaderboard jika game sudah tamat dari awal
else:
    state = "INTRO"

# Sambutan Suara AI
audio.speak("Welcome back, Hunter Ash. Ready to find the artifacts?")

story_index = 0
story_timer = time.time()
scan_progress = 0

# Variabel Mekanik Visual Laser & Waktu Real-Time
laser_y = 80
laser_speed = 4
misi_start_time = 0 
sisa_waktu = 0
warning_played = False  # Flag pencegah spamming suara AI Panic Mode

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
# === KUMPULAN FUNGSI UI CORNER ===
# =========================================================

def teks_tengah(frame, teks, x_start, x_end, y, font, scale, warna, tebal):
    size = cv2.getTextSize(teks, font, scale, tebal)[0]
    lebar_teks = size[0]
    lebar_kotak = x_end - x_start
    x_terpusat = x_start + (lebar_kotak - lebar_teks) // 2
    cv2.putText(frame, teks, (x_terpusat, y), font, scale, warna, tebal)

def gambar_ui_header(frame, w, h):
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 15), -1)
    cv2.line(frame, (0, 60), (w, 60), (0, 255, 255), 2)
    cv2.putText(frame, "TREASURE HUNTER - Asep Enterprise", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.9, (0, 255, 255), 2)
    
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (40, 40, 40), -1)
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (0, 255, 0), 1)
    cv2.putText(frame, f"XP: {xp} | LVL: {level}", (w-240, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 2)

def gambar_ui_inventory(frame, w, h):
    x1, y1, x2, y2 = 20, h-160, 650, h-80
    cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 20), -1)
    cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 1)
    cv2.putText(frame, "TAS INVENTORY:", (x1+15, y1+25), cv2.FONT_HERSHEY_DUPLEX, 0.6, (0, 255, 0), 1)
    
    teks_tas = ", ".join(daftar_inventory) if len(daftar_inventory) > 0 else "Kosong"
    cv2.putText(frame, teks_tas, (x1+15, y1+55), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1)

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

    # Efek Background Dim Terpusat
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

        # 1. Logika Countdown Timer Sisa Waktu
        terpakai = sekarang - misi_start_time
        sisa_waktu = max(0, misi['durasi'] - terpakai)
        
        if sisa_waktu <= 0:
            state = "GAME_OVER"
            audio.speak("Time is up! Mission failed.")

        # 2. AI Panic Mode Warning (Dipanggil sekali saat sisa waktu < 5 detik)
        if sisa_waktu <= 5 and not warning_played and sisa_waktu > 0:
            audio.speak("Warning! Time is running out!")
            warning_played = True

        # 3. Animasi Sci-Fi Scan Line (Laser Bergerak)
        laser_y += laser_speed
        if laser_y >= (h - 180) or laser_y <= 80:
            laser_speed = -laser_speed
            
        cv2.line(frame, (30, laser_y), (w-30, laser_y), (0, 255, 0), 2)

        # Panel HUD Info Misi
        cv2.rectangle(frame, (20, 80), (480, 220), (30, 30, 30), -1)
        cv2.rectangle(frame, (20, 80), (480, 220), (0, 200, 255), 2)

        cv2.putText(frame, f"{misi['judul']}", (35, 115), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1)
        cv2.putText(frame, misi['deskripsi'], (35, 145), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)
        cv2.putText(frame, f"Petunjuk: {misi['petunjuk']}", (35, 175), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1)
        
        # Render Indikator Sisa Waktu Terbuka
        warna_timer = (0, 0, 255) if sisa_waktu < 5 else (0, 255, 255)
        cv2.putText(frame, f"SISA WAKTU: {int(sisa_waktu)}s", (35, 205), cv2.FONT_HERSHEY_DUPLEX, 0.55, warna_timer, 2)

        # Hitung Scan Progress OpenCV Detector
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

        teks_tengah(frame, "OBJEK TERIDENTIFIKASI!", x1, x2, y1+45, cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 0), 2)
        teks_tengah(frame, f"REWARD AWAL: +{misi['xp']} XP", x1, x2, y1+95, cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 255), 1)
        teks_tengah(frame, f"BONUS WAKTU: +{int(sisa_waktu) * 10} XP", x1, x2, y1+125, cv2.FONT_HERSHEY_SIMPLEX, 0.65, (0, 255, 0), 1)
        teks_berkedip_tengah(frame, ">>> TEKAN SPASI UNTUK KLAIM HADIYAH <<<", x1, x2, y1+180, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 2)

    # === STATE: GAME OVER / TAMAT ===
    elif state == "GAME_OVER":
        x1, y1, x2, y2 = w//2-300, h//2-180, w//2+300, h//2+180
        cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 40), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (255, 215, 0), 3)
        
        if misi_index >= len(misi_list):
            teks_tengah(frame, "ALL MISI COMPLETED!", x1, x2, y1+40, cv2.FONT_HERSHEY_DUPLEX, 0.9, (255, 215, 0), 2)
            
            # --- TAMPILAN LOCAL LEADERBOARD ---
            teks_tengah(frame, "=== TOP 3 SPEEDRUN ===", x1, x2, y1+90, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 1)
            for idx, skor in enumerate(top_skor_list):
                nama_player, waktu = skor
                teks_skor = f"#{idx+1} {nama_player} - {waktu:.2f} detik"
                teks_tengah(frame, teks_skor, x1, x2, y1+120+(idx*25), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)
                
            teks_tengah(frame, f"Waktu Kamu: {total_waktu_bermain:.2f}s", x1, x2, y1+210, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2)
        else:
            teks_tengah(frame, "GAME OVER - TIME UP", x1, x2, y1+50, cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 0, 255), 2)
            teks_tengah(frame, f"Gagal di Misi ke-{misi_index+1}", x1, x2, y1+110, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (200, 200, 200), 1)

        teks_tengah(frame, f"TOTAL XP AKHIR: {xp}", x1, x2, y1+250, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
        teks_berkedip_tengah(frame, ">>> TEKAN 'R' UNTUK MENGULANG GAME <<<", x1, x2, y1+300, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0, 255, 255), 2)

    cv2.imshow('Treasure Hunter - Asep enterprise', frame)
    key = cv2.waitKey(1) & 0xFF

    if key == ord('q'):
        break
    
    # === FITUR RESET GAME (KEMBALI KE NOL) ===
    elif key == ord('r') or key == ord('R'):
        if state == "GAME_OVER":
            conn = sqlite3.connect(db.db_path)
            cursor = conn.cursor()
            cursor.execute('DELETE FROM inventory')
            conn.commit()
            conn.close()
            
            db.save_game(0, 1, 0)
            
            xp, level, misi_index = 0, 1, 0
            daftar_inventory = []
            scan_progress = 0
            story_index = 0
            story_timer = time.time()
            warning_played = False
            skor_tercatat = False
            top_skor_list = []
            state = "INTRO"
            audio.speak("System reset. Let's start over.")
            print("[DB] Game berhasil di-reset ke nol!")

    # === LOGIKA AKSI TOMBOL SPASI ===
    elif key == ord(' '):  
        if state == "INTRO" and story_index >= len(story):
            state = "MISI"
            scan_progress = 0
            warning_played = False
            skor_tercatat = False
            misi_start_time = time.time()  # Start timer misi 1
            game_start_time = time.time()  # Start pencatatan waktu speedrun global
        elif state == "SUKSES":
            misi_sekarang = misi_list[misi_index]
            
            # Hitung XP + Akumulasi Time Bonus
            bonus_xp = int(sisa_waktu) * 10
            total_xp_didapat = misi_sekarang['xp'] + bonus_xp
            
            xp += total_xp_didapat
            level = 1 + (xp // 100)
            
            audio.speak(f"Success! You obtained {misi_sekarang['hadiah_item']} with {int(sisa_waktu)} seconds left.")
            
            db.tambah_ke_inventory(misi_sekarang['hadiah_item'], f"Didapat dari {misi_sekarang['judul']}")
            db.save_game(xp, level, misi_index + 1)
            daftar_inventory = db.ambil_all_inventory()
            
            warning_played = False 
            misi_index += 1
            scan_progress = 0
            
            if misi_index >= len(misi_list):
                state = "GAME_OVER"
                total_waktu_bermain = time.time() - game_start_time # Hitung total waktu bersih speedrun
                
                audio.speak("Congratulations! All missions completed. Family economy successfully carried!")
                
                # Masukkan ke leaderboard secara lokal jika belum tercatat di sesi tamat ini
                if not skor_tercatat:
                    db.simpan_skor_leaderboard("ASH", xp, total_waktu_bermain)
                    top_skor_list = db.ambil_top_skor(3)
                    skor_tercatat = True
            else:
                state = "MISI"
                misi_start_time = time.time()  # Reset benchmark timer untuk misi berikutnya

cap.release()
cv2.destroyAllWindows()