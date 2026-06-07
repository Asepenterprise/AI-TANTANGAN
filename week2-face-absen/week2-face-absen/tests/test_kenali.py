import cv2
import face_recognition
import os
import numpy as np
import time
import threading

# KAMERA DULU
cap = cv2.VideoCapture(0)
time.sleep(2)

# Load dataset di background
dataset_wajah = []
dataset_nama = []
dataset_siap = False

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
                print(f"✅ {nama} - {foto}")
            except:
                pass
    dataset_siap = True
    print(f"Dataset siap! {len(dataset_wajah)} wajah")

# Jalankan load dataset di background
threading.Thread(target=load_dataset).start()

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
            if True in hasil:
                index = hasil.index(True)
                nama = dataset_nama[index]

            top, right, bottom, left = [x*4 for x in lokasi_wajah]
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 255, 0), 2)
            cv2.putText(frame, nama, (left, top-10),
                       cv2.FONT_HERSHEY_SIMPLEX, 0.8, (0, 255, 0), 2)

    cv2.imshow('Face Recognition', frame)
    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()