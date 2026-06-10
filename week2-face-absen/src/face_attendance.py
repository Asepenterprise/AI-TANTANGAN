import cv2
import face_recognition
import mediapipe as mp
import os
import numpy as np
import pygame
from gtts import gTTS
import time
import threading
import csv
import math
from datetime import datetime

cap = cv2.VideoCapture(0)
time.sleep(2)

CYAN = (255, 255, 0)
GREEN = (0, 255, 0)
RED = (0, 0, 255)
WHITE = (255, 255, 255)

mp_face_mesh = mp.solutions.face_mesh
face_mesh = mp_face_mesh.FaceMesh(
    min_detection_confidence=0.5,
    min_tracking_confidence=0.5
)
mp_draw = mp.solutions.drawing_utils
mp_style = mp.solutions.drawing_styles

def gambar_lingkaran_hud(frame, cx, cy, radius, warna, tebal=1):
    cv2.circle(frame, (cx, cy), radius, warna, tebal)
    for sudut in [0, 90, 180, 270]:
        rad = math.radians(sudut)
        x = int(cx + radius * math.cos(rad))
        y = int(cy + radius * math.sin(rad))
        cv2.circle(frame, (x, y), 4, warna, -1)

def gambar_kotak_hud(frame, left, top, right, bottom, warna):
    panjang = 20
    tebal = 2
    cv2.line(frame, (left, top), (left + panjang, top), warna, tebal)
    cv2.line(frame, (left, top), (left, top + panjang), warna, tebal)
    cv2.line(frame, (right, top), (right - panjang, top), warna, tebal)
    cv2.line(frame, (right, top), (right, top + panjang), warna, tebal)
    cv2.line(frame, (left, bottom), (left + panjang, bottom), warna, tebal)
    cv2.line(frame, (left, bottom), (left, bottom - panjang), warna, tebal)
    cv2.line(frame, (right, bottom), (right - panjang, bottom), warna, tebal)
    cv2.line(frame, (right, bottom), (right, bottom - panjang), warna, tebal)

def gambar_confidence_circle(frame, cx, cy, confidence, warna):
    cv2.circle(frame, (cx, cy), 40, warna, 1)
    sudut = int(360 * confidence / 100)
    for i in range(sudut):
        rad = math.radians(i - 90)
        x = int(cx + 40 * math.cos(rad))
        y = int(cy + 40 * math.sin(rad))
        cv2.circle(frame, (x, y), 2, warna, -1)
    cv2.putText(frame, f"{int(confidence)}%", (cx-20, cy+5),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, warna, 1)

def gambar_scanline(frame, t):
    h, w, _ = frame.shape
    y = int((t % 2) / 2 * h)
    overlay = frame.copy()
    cv2.line(overlay, (0, y), (w, y), (200, 255, 200), 1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

def catat_absen(nama):
    waktu = datetime.now()
    tanggal = waktu.strftime("%Y-%m-%d")
    jam = waktu.strftime("%H:%M:%S")
    if not os.path.exists('data/absensi.csv'):
        with open('data/absensi.csv', 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow(['Nama', 'Tanggal', 'Jam'])
    with open('data/absensi.csv', 'a', newline='') as f:
        writer = csv.writer(f)
        writer.writerow([nama, tanggal, jam])
    print(f"✅ {nama} absen pada {tanggal} {jam}")

def simpan_foto(nama, frame):
    waktu = datetime.now().strftime("%Y%m%d_%H%M%S")
    folder_bukti = f"data/bukti/{nama}"
    os.makedirs(folder_bukti, exist_ok=True)
    cv2.imwrite(f"{folder_bukti}/{waktu}.jpg", frame)

def sambut(nama):
    def play():
        teks = f"Selamat datang, {nama}"
        tts = gTTS(text=teks, lang='id')
        tts.save(f"data/sambut_{nama}.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load(f"data/sambut_{nama}.mp3")
        pygame.mixer.music.play()
    threading.Thread(target=play).start()

dataset_wajah = []
dataset_nama = []
dataset_siap = False
sudah_absen = []

def load_dataset():
    global dataset_wajah, dataset_nama, dataset_siap
    folder_dataset = "dataset"
    for nama in os.listdir(folder_dataset):
        folder_orang = f"{folder_dataset}/{nama}"
        if not os.path.isdir(folder_orang):
            continue
        for foto in os.listdir(folder_orang):
            path_foto = f"{folder_orang}/{foto}"
            gambar = face_recognition.load_image_file(path_foto)
            try:
                encoding = face_recognition.face_encodings(gambar)[0]
                dataset_wajah.append(encoding)
                dataset_nama.append(nama)
            except:
                pass
    dataset_siap = True
    print(f"Dataset siap! {len(dataset_wajah)} wajah")

threading.Thread(target=load_dataset).start()
os.makedirs("data", exist_ok=True)

frame_count = 0
lokasi = []
encodings = []
confidence = 0

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    frame_count += 1
    h, w, _ = frame.shape
    t = time.time()

    # Simpan frame asli untuk face recognition
    frame_asli = frame.copy()

    overlay = frame.copy()
    #cv2.rectangle(overlay, (0, 0), (w, h), (20, 20, 20), -1)
    cv2.addWeighted(overlay, 0.3, frame, 0.7, 0, frame)

    rgb_mesh = cv2.cvtColor(frame_asli, cv2.COLOR_BGR2RGB)
    hasil_mesh = face_mesh.process(rgb_mesh)
    if hasil_mesh.multi_face_landmarks:
        for face_landmarks in hasil_mesh.multi_face_landmarks:
            mp_draw.draw_landmarks(
                frame,
                face_landmarks,
                mp_face_mesh.FACEMESH_TESSELATION,
                landmark_drawing_spec=None,
                connection_drawing_spec=mp_style.get_default_face_mesh_tesselation_style()
            )

    gambar_scanline(frame, t)

    #cv2.rectangle(frame, (0, 0), (w, 50), (30, 30, 30), -1)
    cv2.putText(frame, "ABSENSI WAJAH", (10, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7, CYAN, 2)
    waktu_str = datetime.now().strftime("%H:%M:%S")
    cv2.putText(frame, waktu_str, (w-100, 30),
               cv2.FONT_HERSHEY_SIMPLEX, 0.7,CYAN, 2)

    if not dataset_siap:
        cv2.putText(frame, "LOADING DATASET...", (w//2-150, h//2),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, CYAN, 2)
    else:
        if frame_count % 5 == 0:
            kecil = cv2.resize(frame_asli, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(kecil, cv2.COLOR_BGR2RGB)
            lokasi = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, lokasi)

        for encoding, lokasi_wajah in zip(encodings, lokasi):
            hasil = face_recognition.compare_faces(dataset_wajah, encoding)
            nama = "TIDAK DIKENAL"
            confidence = 0

            if True in hasil:
                index = hasil.index(True)
                jarak = face_recognition.face_distance(dataset_wajah, encoding)
                confidence = (1 - jarak[index]) * 100
                if confidence >= 55:
                    nama = dataset_nama[index].upper()

            top, right, bottom, left = [x*4 for x in lokasi_wajah]
            cx = (left + right) // 2
            cy = (top + bottom) // 2
            warna = GREEN if nama != "TIDAK DIKENAL" else RED

            gambar_kotak_hud(frame, left, top, right, bottom, warna)
            r_anim = int(40 + 10 * math.sin(t * 2))
            gambar_lingkaran_hud(frame, cx, cy, r_anim + 60, warna)

            if confidence > 0:
                gambar_confidence_circle(frame, right + 50, cy, confidence, warna)

            cv2.putText(frame, nama, (left, top - 15),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.7, warna, 2)
            status = "IDENTIFIED" if nama != "TIDAK DIKENAL" else "MEMINDAI..."
            cv2.putText(frame, status, (left, bottom + 20),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.5, warna, 1)

            if nama != "TIDAK DIKENAL" and nama.title() not in sudah_absen:
                catat_absen(nama.title())
                simpan_foto(nama.title(), frame)
                sambut(nama.title())
                sudah_absen.append(nama.title())

    
    #cv2.rectangle(frame, (0, h-120), (w, h), (30, 30, 30), -1)
    cv2.putText(frame, f"DAFTAR ORANG: {len(sudah_absen)}", (10, h-95),
               cv2.FONT_HERSHEY_SIMPLEX, 0.5, CYAN, 1)
    for i, orang in enumerate(sudah_absen[:3]):
        cv2.putText(frame, f">> {orang.upper()}", (10, h-70 + i*22),
                   cv2.FONT_HERSHEY_SIMPLEX, 0.45, CYAN, 1)
    for i in range(20):
        bar_h = int(30 * abs(math.sin(t + i * 0.3)))
        cv2.rectangle(frame, (w-220 + i*10, h-10),
                     (w-215 + i*10, h-10-bar_h), CYAN, -1)

    cv2.imshow('ABSEN WAJAH', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()