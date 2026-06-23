import pyttsx3
import threading

class GameAudio:
    def __init__(self):
        # Inisialisasi engine di main thread untuk setup suara default
        self.engine = pyttsx3.init()
        voices = self.engine.getProperty('voices')
        if len(voices) > 1:
            self.engine.setProperty('voice', voices[1].id) # Pakai suara perempuan jika tersedia
        self.engine.setProperty('rate', 175)

    def _speak_worker(self, text):
        """Fungsi pekerja yang berjalan di dalam thread terpisah"""
        engine_thread = pyttsx3.init()
        voices = engine_thread.getProperty('voices')
        if len(voices) > 1:
            engine_thread.setProperty('voice', voices[1].id)
        engine_thread.setProperty('rate', 175)
        engine_thread.say(text)
        engine_thread.runAndWait()

    def speak(self, text):
        """Memanggil asisten suara secara asinkronus (tidak membuat frame freeze)"""
        t = threading.Thread(target=self._speak_worker, args=(text,))
        t.daemon = True
        t.start()