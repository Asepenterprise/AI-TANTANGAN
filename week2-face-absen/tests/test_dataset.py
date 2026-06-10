import cv2
import os

nama = input ("Masukkan nama kamu: ")

folder = f"dataset/{nama}"
os.makedirs(folder, exist_ok=True)
print(f"Folder {folder} siap!")

cap = cv2.VideoCapture(0)
foto_ke = 1

print("Tekan 's' untuk Foto, dan tekan 'q' Untuk keluar")

while True:
    ret, frame = cap.read()
    if not ret:
        continue

    frame = cv2.flip(frame ,1)
    
    key = cv2.waitKey(1) & 0XFF

    teks = f"Tekan S untuk foto | Foto ke: {foto_ke}"
    cv2.putText(frame, teks, (50, 50),
                cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
    cv2.imshow('Daftar Wajah', frame)
    


    if key == ord ('s'):
        nama_file = f"{folder}/fot_{foto_ke}.jpg"
        cv2.imwrite(f"{folder}/foto_{foto_ke}.jpg", frame)
        print(f"Foto {foto_ke} Tersimpan!")
        foto_ke += 1

    elif key == ord ('q'):
        break


cap.release()
cv2.destroyAllWindows()
        










