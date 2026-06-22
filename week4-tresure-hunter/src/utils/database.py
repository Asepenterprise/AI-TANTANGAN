import sqlite3
import os

class GameDatabase:
    def __init__(self, db_path="data/savegame.db"):
        self.db_path = db_path
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self.init_db() # Jalankan pembuatan tabel saat database diakses

    def init_db(self):
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()

        # 1. Tabel Progress Player
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS player_progress (
                id INTEGER PRIMARY KEY,
                xp INTEGER DEFAULT 0,
                level INTEGER DEFAULT 1,
                current_misi_index INTEGER DEFAULT 0
            )
        ''')
        
        # 2. Tabel Inventory Tas
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS inventory (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama_item TEXT UNIQUE,
                deskripsi TEXT
            )
        ''')
        
        # 3. Tabel Leaderboard Skor (DITAMBAHKAN DISINI)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS leaderboard (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                nama TEXT,
                total_xp INTEGER,
                waktu_total REAL,
                tanggal TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Inisialisasi data awal jika game baru pertama kali dijalankan
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
        data = cursor.fetchone()
        conn.close()
        return data
    
    def tambah_ke_inventory(self, nama_item, deskripsi):
        """Memasukkan artefak baru ke dalam database tas"""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            cursor.execute('INSERT INTO inventory (nama_item, deskripsi) VALUES (?, ?)', (nama_item, deskripsi))
            conn.commit()
            conn.close()
            print(f"[DB] {nama_item} ditambahkan ke Inventory!")
        except sqlite3.IntegrityError:
            pass

    def ambil_all_inventory(self):
        """Mengambil semua item yang dimiliki player untuk ditampilkan di HUD"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT nama_item FROM inventory')
        items = cursor.fetchall()
        conn.close()
        return [item[0] for item in items]

    def simpan_skor_leaderboard(self, nama, total_xp, waktu_total):
        """Menyimpan rekor waktu tamat ke database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO leaderboard (nama, total_xp, waktu_total)
            VALUES (?, ?, ?)
        ''', (nama, total_xp, waktu_total))
        conn.commit()
        conn.close()
        print(f"[DB] Skor baru berhasil dicatat: {waktu_total:.2f} detik.")

    def ambil_top_skor(self, limit=3):
        """Mengambil rekor waktu tercepat"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT nama, waktu_total FROM leaderboard 
            ORDER BY waktu_total ASC LIMIT ?
        ''', (limit,))
        data = cursor.fetchall()
        conn.close()
        return data