import pyttsx3
import threading

class GameAudio:
    def __init__(self):
        # Inisialisasi engine pyttsx3
        self.engine = pyttsx3.init()
        
        # Mengatur kecepatan bicara (default biasanya 200, kita lambatin dikit biar keren)
        self.engine.setProperty('rate', 165)
        
        # Mengatur volume (0.0 sampai 1.0)
        self.engine.setProperty('volume', 1.0)

    def _speak_worker(self, teks):
        """Fungsi internal yang berjalan di dalam thread terpisah"""
        try:
            self.engine.say(teks)
            self.engine.runAndWait()
        except Exception as e:
            print(f"[AUDIO ERROR] Gagal mengeluarkan suara: {e}")

    def speak(self, teks):
        """Panggil fungsi ini dari luar untuk berbicara tanpa membuat game freeze"""
        # Kita buat Thread baru setiap kali robot mau ngomong
        threading.Thread(target=self._speak_worker, args=(teks,), daemon=True).start()