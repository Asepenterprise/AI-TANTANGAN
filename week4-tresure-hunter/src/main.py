import cv2
import numpy as np
import time
import sqlite3 
import os
import math
import threading
import pygame
import subprocess
from datetime import datetime
from gtts import gTTS

# =====================================================================
# CONFIG SMART FALLBACK (SANGAT RAMAH INTEL CELERON)
# =====================================================================
MOCK_MODE = True  # Ubah ke False jika lu main di laptop i3/i5/i7/Ryzen

if not MOCK_MODE:
    import mediapipe.solutions.hands as mp_hands
    import mediapipe.solutions.pose as mp_pose
    import mediapipe.solutions.face_mesh as mp_face_mesh
    import mediapipe.solutions.drawing_utils as mp_draw
    import mediapipe.solutions.drawing_styles as mp_style
else:
    print("[SYSTEM] Running in Celeron Mock Mode. MediaPipe bypassed safely.")

from vision.detector import TargetDetector
from utils.database import GameDatabase
from utils.audio import GameAudio 
from utils.visual import tempel_png_transparan 

# === CONFIG MISI & WARNA ===
misi_list = [
    {
        "id": 1,
        "judul": "ARTEFAK PERTAMA",
        "deskripsi": "Temukan dinding rahasia di rumahmu!",
        "petunjuk": "Arahkan kamera ke dinding berwarna Hijau",
        "hsv_lower": [60, 40, 40],
        "hsv_upper": [90, 255, 255],
        "xp": 50,
        "hadiah_item": "Kunci Kuno Emas",
        "durasi": 25
    },
    {
        "id": 2,
        "judul": "ARTEFAK KEDUA (RED CORE)",
        "deskripsi": "Cari energi merah di sekitarmu!",
        "petunjuk": "Arahkan kamera ke benda Merah Terang",
        "hsv_lower": [0, 120, 70],
        "hsv_upper": [10, 255, 255],
        "xp": 100,
        "hadiah_item": "Kristal Merah Koron",
        "durasi": 20
    },
    {
        "id": 3,
        "judul": "ARTEFAK KETIGA (BLUE MYSTIC)",
        "deskripsi": "Cari energi biru kuno di dekatmu!",
        "petunjuk": "Arahkan kamera ke benda berwarna Biru",
        "hsv_lower": [100, 150, 50],
        "hsv_upper": [140, 255, 255],
        "xp": 150,
        "hadiah_item": "Plakat Biru Atlantis",
        "durasi": 20
    }
]

# === INITIALIZATION BASE SYSTEM ===
cap = cv2.VideoCapture(0)
cap.set(cv2.CAP_PROP_FRAME_WIDTH, 1280)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 720)
time.sleep(1)

if not cap.isOpened():
    print("[ERROR] Kamera gagal terhubung!")
    exit()

detector = TargetDetector()
db = GameDatabase()
audio = GameAudio() 
pygame.mixer.init()

# === INITIALIZATION MEDIAPIPE PIPELINES ===
if not MOCK_MODE:
    hands = mp_hands.Hands(min_detection_confidence=0.7, min_tracking_confidence=0.7)
    pose = mp_pose.Pose(min_detection_confidence=0.5, min_tracking_confidence=0.5, model_complexity=0)
    face_mesh = mp_face_mesh.FaceMesh(min_detection_confidence=0.5, min_tracking_confidence=0.5)

# === LOAD ASSETS & DATA ===
path_avatar = "data/assets/avatar_ash.png"
avatar_img = cv2.imread(path_avatar, cv2.IMREAD_UNCHANGED) if os.path.exists(path_avatar) else None

saved_xp, saved_level, saved_misi_index = db.load_game()
xp, level, misi_index = saved_xp, saved_level, saved_misi_index
daftar_inventory = db.ambil_all_inventory()

# === SYSTEM VARIABLES ===
state = "GESTURE_INTRO"  
game_start_time = 0
total_waktu_bermain = 0
skor_tercatat = False
top_skor_list = []
frame_count = 0

# Variables: Gesture
ily_tahap = 0
menu_cooldown = 0
ujung_jari = [8, 12, 16, 20]
ujung_pangkal = [6, 10, 14, 18]

# Variables: Biometric Face
face_lock_start = None

# Variables: Game & Gym
scan_progress = 0
laser_y = 80
laser_speed = 6
misi_start_time = 0 
sisa_waktu = 0
warning_played = False
gym_mode = "PUSHUP"
pushup_counter, squat_counter = 0, 0
pushup_status, squat_status = "UP", "UP"
plank_aktif, plank_mulai, plank_total = False, None, 0
suara_cooldown = 0

# === AUDIO ENGINE SYNTHESIS ===
suara_list = {
    "g_intro": "data/audio_intro.mp3",
    "g_key": "data/audio_gesture_key.mp3",
    "g_akses": "data/audio_akses.mp3",
    "g_scan": "data/audio_scanning.mp3"
}

def speak_sync(text_msg, file_path):
    if not os.path.exists(file_path):
        os.makedirs("data", exist_ok=True)
        tts = gTTS(text=text_msg, lang='id')
        tts.save(file_path)
    def play():
        try:
            if pygame.mixer.music.get_busy(): pygame.mixer.music.stop()
            pygame.mixer.music.load(file_path)
            pygame.mixer.music.play()
        except: pass
    threading.Thread(target=play).start()

speak_sync("Selamat datang tuan muda Ashraf, silakan masukkan gesture rahasia", suara_list["g_intro"])

# === HELPER UI FUNCTIONS ===
def teks_tengah(frame, teks, x_start, x_end, y, font, scale, warna, tebal):
    size = cv2.getTextSize(teks, font, scale, tebal)[0]
    x_terpusat = x_start + ((x_end - x_start) - size[0]) // 2
    cv2.putText(frame, teks, (x_terpusat, y), font, scale, warna, tebal, cv2.LINE_AA)

def gambar_ui_header(frame, w, h):
    cv2.rectangle(frame, (0, 0), (w, 60), (15, 15, 15), -1)
    cv2.line(frame, (0, 60), (w, 60), (0, 255, 255), 2)
    cv2.putText(frame, "TREASURE HUNTER ARCHADE EDITION", (20, 40), cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2, cv2.LINE_AA)
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (40, 40, 40), -1)
    cv2.rectangle(frame, (w-260, 15), (w-20, 45), (0, 255, 0), 1)
    cv2.putText(frame, f"XP: {xp} | LVL: {level}", (w-240, 36), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 2, cv2.LINE_AA)

def gambar_ui_inventory(frame, w, h):
    cv2.rectangle(frame, (20, h-160), (650, h-80), (20, 20, 20), -1)
    cv2.rectangle(frame, (20, h-160), (650, h-80), (0, 255, 0), 1)
    str_inventory = "TAS INVENTORY: " + (", ".join(daftar_inventory) if daftar_inventory else "Kosong")
    cv2.putText(frame, str_inventory, (35, h-115), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (220, 220, 220), 1, cv2.LINE_AA)

def deteksi_jari(lm):
    jari = [lm[4].x < lm[3].x]
    for ujung, pangkal in zip(ujung_jari, ujung_pangkal):
        jari.append(lm[ujung].y < lm[pangkal].y)
    return jari

def hitung_sudut(a, b, c):
    a, b, c = np.array(a), np.array(b), np.array(c)
    ba, bc = a - b, c - b
    cosine = np.dot(ba, bc) / (np.linalg.norm(ba) * np.linalg.norm(bc))
    return np.degrees(np.arccos(np.clip(cosine, -1.0, 1.0)))

# === MAIN SYSTEM LOOP ===
while True:
    ret, frame = cap.read()
    if not ret or frame is None: continue

    frame = cv2.flip(frame, 1)
    h, w, _ = frame.shape
    sekarang = time.time()
    frame_count += 1

    # Shading Background Efek Cyberpunk
    overlay = frame.copy()
    cv2.rectangle(overlay, (0, 0), (w, h), (15, 10, 25), -1)
    cv2.addWeighted(overlay, 0.25, frame, 0.75, 0, frame)

    gambar_ui_header(frame, w, h)
    gambar_ui_inventory(frame, w, h)

    # Ambil input key di awal biar responsive
    key = cv2.waitKey(1) & 0xFF

    # ----------------------------------------------------
    # [PROJECT 1 STATE]: SECURITY GESTURE RAHASIA
    # ----------------------------------------------------
    if state == "GESTURE_INTRO":
        cv2.rectangle(frame, (50, 90), (w-50, h-190), (15, 15, 15), -1)
        cv2.rectangle(frame, (50, 90), (w-50, h-190), (0, 255, 255), 2)
        teks_tengah(frame, "SECURITY GATEWAY: LOCK SYSTEMS", 50, w-50, 130, cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 0, 255), 2)
        
        if MOCK_MODE:
            cv2.putText(frame, "[CELERON MODE] Tekan 'C' untuk Bypass Gesture", (70, h-220), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 165, 255), 1)

        warna_i = (0, 255, 0) if ily_tahap >= 1 else (100, 100, 100)
        warna_l = (0, 255, 0) if ily_tahap >= 2 else (100, 100, 100)
        warna_y = (0, 255, 0) if ily_tahap >= 3 else (100, 100, 100)
        cv2.putText(frame, "I", (w//2 - 90, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.3, warna_i, 3)
        cv2.putText(frame, "LOVE", (w//2 - 30, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.3, warna_l, 3)
        cv2.putText(frame, "YOU", (w//2 + 80, 210), cv2.FONT_HERSHEY_SIMPLEX, 1.3, warna_y, 3)

        if not MOCK_MODE:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hasil_tangan = hands.process(frame_rgb)
            if hasil_tangan.multi_hand_landmarks:
                for hand_lm in hasil_tangan.multi_hand_landmarks:
                    mp_draw.draw_landmarks(frame, hand_lm, mp_hands.HAND_CONNECTIONS)
                    jari = deteksi_jari(hand_lm.landmark)
                    if ily_tahap == 0 and jari == [False, False, False, False, True]: ily_tahap = 1
                    elif ily_tahap == 1 and jari == [True, True, False, False, False]: ily_tahap = 2
                    elif ily_tahap == 2 and jari == [True, True, False, False, True]:
                        ily_tahap = 3
                        state = "BIOMETRIC_SCAN"
                        speak_sync("Akses gesture diterima. Memulai pemindaian wajah biometrik.", suara_list["g_key"])
                        face_lock_start = sekarang
        else:
            # Fallback Celeron Simulation
            if key == ord('c') or key == ord('C'):
                ily_tahap = 3
                state = "BIOMETRIC_SCAN"
                speak_sync("Akses gesture diterima. Memulai pemindaian wajah biometrik.", suara_list["g_key"])
                face_lock_start = sekarang

    # ----------------------------------------------------
    # [PROJECT 2 STATE]: LITE BIOMETRIC SCAN
    # ----------------------------------------------------
    elif state == "BIOMETRIC_SCAN":
        teks_tengah(frame, "SYSTEM SCANNING: DETEKSI WAJAH USER", 50, w-50, 110, cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 255, 255), 2)
        
        y_scan = int((sekarang % 2) / 2 * h)
        cv2.line(frame, (50, y_scan), (w-50, y_scan), (0, 255, 0), 2)

        if not MOCK_MODE:
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hasil_mesh = face_mesh.process(frame_rgb)
            if hasil_mesh.multi_face_landmarks:
                for f_lm in hasil_mesh.multi_face_landmarks:
                    mp_draw.draw_landmarks(frame, f_lm, None, landmark_drawing_spec=None, connection_drawing_spec=mp_style.get_default_face_mesh_tesselation_style())
                waktu_scan = sekarang - face_lock_start
                if waktu_scan < 3.0:
                    teks_tengah(frame, f"MENGANALISA STRUKTUR WAJAH... {int(waktu_scan/3*100)}%", 50, w-50, h//2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 140, 255), 2)
                else:
                    state = "MISI"
                    misi_start_time = sekarang
                    game_start_time = sekarang
                    audio.speak("Identity Verified. Welcome back Agent Ash. Mission Start!")
            else:
                teks_tengah(frame, "WAJAH TIDAK TERDETEKSI! HADAP KAMERA!", 50, w-50, h//2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        else:
            # Fallback Celeron Simulation (Otomatis Scan setelah 3 detik)
            waktu_scan = sekarang - face_lock_start
            if waktu_scan < 3.0:
                teks_tengah(frame, f"[CELERON MOCK] BERHASIL MENGANALISA STRUKTUR WAJAH... {int(waktu_scan/3*100)}%", 50, w-50, h//2, cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
            else:
                state = "MISI"
                misi_start_time = sekarang
                game_start_time = sekarang
                audio.speak("Identity Verified. Welcome back Agent Ash. Mission Start!")

    # ----------------------------------------------------
    # [CORE STATE]: TREASURE HUNTER COLOR ADVENTURE
    # ----------------------------------------------------
    elif state == "MISI":
        misi = misi_list[misi_index]
        
        if avatar_img is not None:
            frame = tempel_png_transparan(frame, avatar_img, x=35, y=95, ukuran_baru=(120, 120))
        else:
            cv2.rectangle(frame, (35, 95), (155, 215), (40, 40, 40), -1)

        cv2.rectangle(frame, (175, 95), (650, 235), (20, 20, 20), -1)
        cv2.rectangle(frame, (175, 95), (650, 235), (0, 200, 255), 2)
        cv2.putText(frame, f"{misi['judul']}", (190, 130), cv2.FONT_HERSHEY_DUPLEX, 0.65, (0, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, misi['deskripsi'], (190, 160), cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1, cv2.LINE_AA)
        cv2.putText(frame, f"Petunjuk: {misi['petunjuk']}", (190, 185), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 0), 1, cv2.LINE_AA)

        sisa_waktu = max(0, misi['durasi'] - (sekarang - misi_start_time))
        warna_t = (0, 0, 255) if sisa_waktu < 6 else (0, 255, 255)
        cv2.putText(frame, f"SISA WAKTU: {int(sisa_waktu)}s", (190, 215), cv2.FONT_HERSHEY_DUPLEX, 0.55, warna_t, 2, cv2.LINE_AA)

        cv2.putText(frame, "Tekan 'G' untuk aktifkan GYM TIME BOOST", (20, h-180), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)

        if sisa_waktu <= 0: state = "GAME_OVER"; audio.speak("Time is up! Mission failed.")

        # FITUR UTAMA BERBURU WARNA TETAP PAKAI KAMERA DI CELERON
        persen = detector.hitung_persen_warna(frame, misi["hsv_lower"], misi["hsv_upper"])
        scan_progress = min(scan_progress + 2, 100) if persen > 8 else max(scan_progress - 1.5, 0)

        bar_w = int((w-100) * scan_progress / 100)
        cv2.rectangle(frame, (50, h-60), (w-50, h-25), (40, 40, 40), -1)
        if scan_progress > 0:
            cv2.rectangle(frame, (50, h-60), (50+bar_w, h-25), (0, 255, 0) if scan_progress > 75 else (0, 255, 255), -1)
        teks_tengah(frame, f"MENGANALISA OBJEK... {int(scan_progress)}% | Kamera: {int(persen)}%", 50, w-50, h-37, cv2.FONT_HERSHEY_SIMPLEX, 0.55, (255, 255, 255), 1)

        if scan_progress >= 100: state = "SUKSES"

    # ----------------------------------------------------
    # [PROJECT 3 STATE]: WORKOUT GYM TIME BOOST MODE
    # ----------------------------------------------------
    elif state == "GYM_BOOST":
        cv2.rectangle(frame, (0, 60), (w, 120), (10, 30, 10), -1)
        cv2.line(frame, (0, 120), (w, 120), (0, 255, 0), 2)
        cv2.putText(frame, f"ENERGY BOOST ACTIVE - MODE: {gym_mode}", (20, 95), cv2.FONT_HERSHEY_DUPLEX, 0.75, (0, 255, 0), 2)
        
        if not MOCK_MODE:
            cv2.putText(frame, "P=PushUp   S=Squat   Spasi=Kembali Berburu", (w-500, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (240, 240, 240), 1)
            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
            hasil_pose = pose.process(frame_rgb)

            if hasil_pose and hasil_pose.pose_landmarks:
                mp_draw.draw_landmarks(frame, hasil_pose.pose_landmarks, mp_pose.POSE_CONNECTIONS)
                lm = hasil_pose.pose_landmarks.landmark

                if gym_mode == "PUSHUP":
                    bahu = [lm[11].x * w, lm[11].y * h]
                    siku = [lm[13].x * w, lm[13].y * h]
                    pergelangan = [lm[15].x * w, lm[15].y * h]
                    sudut = hitung_sudut(bahu, siku, pergelangan)
                    if sudut < 90: pushup_status = "DOWN"
                    elif sudut > 160 and pushup_status == "DOWN":
                        pushup_status = "UP"; pushup_counter += 1
                        misi_start_time += 7 
                        if sekarang > suara_cooldown: audio.speak(f"{pushup_counter}"); suara_cooldown = sekarang + 1.5

                elif gym_mode == "SQUAT":
                    pinggul = [lm[23].x * w, lm[23].y * h]
                    lutut = [lm[25].x * w, lm[25].y * h]
                    engkel = [lm[27].x * w, lm[27].y * h]
                    sudut = hitung_sudut(pinggul, lutut, engkel)
                    if sudut < 130: squat_status = "DOWN"
                    elif sudut > 160 and squat_status == "DOWN":
                        squat_status = "UP"; squat_counter += 1
                        misi_start_time += 10 
                        if sekarang > suara_cooldown: audio.speak(f"{squat_counter}"); suara_cooldown = sekarang + 1.5
        else:
            # Fallback Celeron Simulation (Gunakan Tombol 'T' untuk nambah Repetisi Gym)
            cv2.putText(frame, "P=PushUp   S=Squat   [CELETRON] Tekan 'T' buat Tambah Reps   Spasi=Kembali", (w-720, 95), cv2.FONT_HERSHEY_SIMPLEX, 0.45, (0, 255, 255), 1)
            if key == ord('t') or key == ord('T'):
                if gym_mode == "PUSHUP":
                    pushup_counter += 1; misi_start_time += 7
                    audio.speak(f"{pushup_counter}")
                elif gym_mode == "SQUAT":
                    squat_counter += 1; misi_start_time += 10
                    audio.speak(f"{squat_counter}")

        cv2.putText(frame, f"PUSHUP REPS: {pushup_counter}", (50, h-220), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 0), 2)
        cv2.putText(frame, f"SQUAT REPS: {squat_counter}", (50, h-180), cv2.FONT_HERSHEY_DUPLEX, 1.0, (0, 255, 255), 2)

    # ----------------------------------------------------
    # STATE: SUKSES & GAME OVER
    # ----------------------------------------------------
    elif state == "SUKSES":
        x1, y1, x2, y2 = w//2-250, h//2-100, w//2+250, h//2+100
        cv2.rectangle(frame, (x1, y1), (x2, y2), (10, 40, 10), -1)
        cv2.rectangle(frame, (x1, y1), (x2, y2), (0, 255, 0), 3)
        teks_tengah(frame, "ARTEFAK AMAN DIIDENTIFIKASI!", x1, x2, y1+40, cv2.FONT_HERSHEY_DUPLEX, 0.7, (0, 255, 0), 2)
        teks_tengah(frame, ">>> TEKAN SPASI UNTUK AMBIL REWARD <<<", x1, x2, y1+150, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (255, 255, 255), 1)

    elif state == "GAME_OVER":
        x1, y1, x2, y2 = w//2-300, h//2-120, w//2+300, h//2+120
        cv2.rectangle(frame, (x1, y1), (x2, y2), (20, 20, 30), -1)
        teks_tengah(frame, "MISI SELESAI / TAMAT", x1, x2, y1+40, cv2.FONT_HERSHEY_DUPLEX, 0.8, (0, 215, 255), 2)
        teks_tengah(frame, f"TOTAL SKOR XP AKHIR: {xp}", x1, x2, y1+110, cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 0), 1)
        teks_tengah(frame, "Tekan 'R' untuk Reset Ulang Database", x1, x2, y1+180, cv2.FONT_HERSHEY_SIMPLEX, 0.5, (200, 200, 200), 1)

    cv2.imshow('Treasure Hunter - Asep enterprise', frame)

    # --- LOGIKA TOMBOL INPUTS ---
    if key == ord('q'): break
    elif key == ord('p') or key == ord('P'): gym_mode = "PUSHUP"
    elif key == ord('s') or key == ord('S'): gym_mode = "SQUAT"
    elif key == ord('g') or key == ord('G'):
        if state == "MISI": state = "GYM_BOOST"
        
    elif key == ord('r') or key == ord('R'):
        if state == "GAME_OVER":
            conn = sqlite3.connect(db.db_path)
            conn.cursor().execute('DELETE FROM inventory')
            conn.commit(); conn.close()
            db.save_game(0, 1, 0)
            xp, level, misi_index = 0, 1, 0
            daftar_inventory = []
            ily_tahap, scan_progress = 0, 0
            state = "GESTURE_INTRO"
            audio.speak("System Data Reset.")

    elif key == ord(' '):  
        if state == "GYM_BOOST":
            state = "MISI" 
        elif state == "SUKSES":
            misi_sekarang = misi_list[misi_index]
            xp += misi_sekarang['xp']
            level = 1 + (xp // 100)
            
            audio.speak(f"Obtained {misi_sekarang['hadiah_item']}.")
            db.tambah_ke_inventory(misi_sekarang['hadiah_item'], f"Misi {misi_sekarang['id']}")
            db.save_game(xp, level, misi_index + 1)
            daftar_inventory = db.ambil_all_inventory()
            
            misi_index += 1
            scan_progress = 0
            
            if misi_index >= len(misi_list):
                state = "GAME_OVER"
                total_waktu_bermain = time.time() - game_start_time
                db.simpan_skor_leaderboard("ASH", xp, total_waktu_bermain)
            else:
                state = "MISI"
                misi_start_time = time.time()

cap.release()
cv2.destroyAllWindows()