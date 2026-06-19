import sqlite3
import os

class GameDatabase: # Menggunakan PascalCase (D kapital) agar sesuai dengan import di main.py
    def __init__(self, db_path="data/savegame.db"): # 1. Fix __init__
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db() # Jalankan pembuatan tabel saat database diakses

    def init_db(self): # 2. Sekarang posisinya sudah sejajar, tidak masuk ke dalam __init__
        conn = sqlite3.connect(self.db_path) # 3. Fix tanda titik (self.db_path)
        cursor = conn.cursor()

        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_progress (
                id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_misi_index INTEGER DEFAULT 0
            )
        ''')
        
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_item TEXT UNIQUE,
                deskripsi TEXT
            )
        ''')
        
        cursor.execute('SELECT COUNT(*) FROM player_progress')
        if cursor.fetchone()[0] == 0:
            cursor.execute('INSERT INTO player_progress (id, xp, level, current_misi_index) VALUES (1, 0, 1, 0)')

        conn.commit()
        conn.close()

    def save_game(self, xp, level, misi_index):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE player_progress 
            SET xp = ?, level = ?, current_misi_index = ? 
            WHERE id = 1
        ''', (xp, level, misi_index))
        conn.commit()
        conn.close()
        print("[DB] Game Berhasil Disimpan!")

    def load_game(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT xp, level, current_misi_index FROM player_progress WHERE id = 1')
        data = cursor.fetchone() # 4. Fix tambah kurung ()
        conn.close()
        return data
    
    def tambah_ke_inventory(self, nama_item, deskripsi): # Sesuaikan nama dengan yang dipanggil main.py
        """Memasukkan artefak baru ke dalam database tas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO inventory (nama_item, deskripsi) VALUES (?, ?)', (nama_item, deskripsi))
            conn.commit()
            conn.close() # 4. Fix tambah kurung ()
            print(f"[DB] {nama_item} ditambahkan ke Inventory!")
        except sqlite3.IntegrityError: # 5. Fix kapital huruf I
            pass

    def ambil_all_inventory(self):
        """Mengambil semua item yang dimiliki player untuk ditampilkan di HUD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nama_item FROM inventory')
        items = cursor.fetchall() # 4. Fix tambah kurung ()
        conn.close()
        return [item[0] for item in items]