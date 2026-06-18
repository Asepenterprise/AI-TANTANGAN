class Player:
    def __init__(self):
        self.xp = 0
        self.level = 1
        
    def tambah_xp(self, jumlah):
        self.xp += jumlah
        # Formula naik level sederhana: tiap 100 XP
        self.level = 1 + (self.xp // 100)