import cv2
import numpy as np

def tempel_png_transparan(background, overlay, x, y, ukuran_baru=(100, 100)):
    """
    Fungsi untuk menempelkan gambar PNG (baik 3 channel maupun 4 channel)
    ke background pada posisi koordinat (x, y).
    """
    # 1. Resize gambar avatar agar ukurannya pas di HUD (misal: 100x100 pixel)
    overlay = cv2.resize(overlay, ukuran_baru)
    
    h_ol, w_ol, c_ol = overlay.shape
    h_bg, w_bg, _ = background.shape

    # Batasi area agar tidak melebihi ukuran background (layar game)
    if x + w_ol > w_bg or y + h_ol > h_bg or x < 0 or y < 0:
        # Jika koordinat di luar batas layar, abaikan penempelan agar tidak crash
        return background

    # Ambil potongan ROI (Region of Interest) dari background
    roi = background[y:y+h_ol, x:x+w_ol]

    # 2. Jika gambar memiliki channel transparansi (PNG 4 channel)
    if c_ol == 4:
        mask = overlay[:, :, 3] / 255.0
        mask_inv = 1.0 - mask

        for c in range(3):
            roi[:, :, c] = (mask * overlay[:, :, c] + mask_inv * roi[:, :, c])
    else:
        # 3. Jika gambar biasa (3 channel seperti foto Megumi tadi), langsung timpa saja
        background[y:y+h_ol, x:x+w_ol] = overlay

    return background