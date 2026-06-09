
import cv2
import face_recognition
import os
import numpy as np
import pygame
from gtts import gTTS
import time
import threading
import csv
from datetime import datetime

# KAMERA DULU
cap = cv2.VideoCapture(0)
time.sleep(2)

# === FUNGSI ABSEN ===
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

def sambut(nama):
    def play():
        teks = f"Selamat datang, {nama}"
        tts = gTTS(text=teks, lang='id')
        tts.save(f"data_sambut_{nama}.mp3")
        pygame.mixer.init()
        pygame.mixer.music.load(f"data_sambut_{nama}.mp3")
        pygame.mixer.music.play()
    threading.Thread(target=play).start()

# === LOAD DATASET ===
dataset_wajah = []
dataset_nama = []
dataset_siap = False
sudah_absen = []  # cegah double absen

def load_dataset():
    global dataset_wajah, dataset_nama, dataset_siap
    print("LOADING DATASET...")
    folder_dataset = "dataset"
    for nama in os.listdir(folder_dataset):
        folder_orang = f"{folder_dataset}/{nama}"
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

# Buat folder data kalau belum ada
os.makedirs("data", exist_ok=True)

frame_count = 0
lokasi = []
encodings = []

while True:
    ret, frame = cap.read()
    if not ret or frame is None:
        continue

    frame = cv2.flip(frame, 1)
    frame_count += 1

    if not dataset_siap:
        cv2.putText(frame, "Loading dataset...", (10, 50),
                   cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 255), 2)
    else:
        if frame_count % 3 == 0:
            kecil = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)
            rgb = cv2.cvtColor(kecil, cv2.COLOR_BGR2RGB)
            lokasi = face_recognition.face_locations(rgb)
            encodings = face_recognition.face_encodings(rgb, lokasi)

        for encoding, lokasi_wajah in zip(encodings, lokasi):
            hasil = face_recognition.compare_faces(dataset_wajah, encoding)
            nama = "Tidak Dikenal"

            h, w, _ = frame.shape
            overlay = frame.copy()
            cv2.rectangle(overlay, (w-250, 0), (w, len(sudah_absen)*30+60), (0,0,0), -1)
            cv2.addWeighted(overlay, 0.6, frame, 0.4, 0, frame)


            cv2.putText(frame, "DAFTAR KEHADIRAN", (w-240, 30),
                        cv2.FONT_HERSHEY_SIMPLEX, 0.6, (0, 255, 255), 2)
            
            for i, orang in enumerate(sudah_absen):
                cv2.putText(frame, f">> {orang}", (w-240, 60 + i*30),
                            cv2.FONT_HERSHEY_SIMPLEX, 0.5, (0, 255, 0), 1)


            if True in hasil:
                index = hasil.index(True)
                nama = dataset_nama[index]

                # Catat absen kalau belum absen
                if nama not in sudah_absen:
                    catat_absen(nama)
                    sambut(nama)
                    sudah_absen.append(nama)

            top, right, bottom, left = [x*4 for x in lokasi_wajah]
            
            # Warna berbeda untuk yang sudah absen
            warna = (0, 255, 0) if nama in sudah_absen else (0, 0, 255)
            cv2.rectangle(frame, (left, top), (right, bottom), warna, 2)
            cv2.putText(frame, nama, (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, warna, 2)

        # Tampilkan jumlah yang sudah absen
        cv2.putText(frame, f"Hadir: {len(sudah_absen)} orang",
                   (10, 30), cv2.FONT_HERSHEY_SIMPLEX, 0.8, (255, 255, 0), 2)

    cv2.imshow('Face Attendance', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()