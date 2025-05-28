import json
import sqlite3
import os

def init_song_data(db_path="maimai_dx.db"):
    """初始化 SQLite 数据库并导入歌曲数据"""
    if not os.path.exists(db_path):
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                data TEXT
            )
        """)
        with open("maidata.json", "r", encoding="utf-8") as f:
            original_data = json.load(f)
            for song in original_data:
                cursor.execute("INSERT INTO songs (data) VALUES (?)", (json.dumps(song),))
        conn.commit()
        conn.close()

def load_song_data(db_path="maimai_dx.db"):
    """从 SQLite 加载歌曲数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT data FROM songs")
    original_data = [json.loads(row[0]) for row in cursor.fetchall()]
    conn.close()

    split_data = []
    for song in original_data:
        std_row = {
            "chart_type": "std",
            "title": song.get("title"),
            "artist": song.get("artist"),
            "category": song.get("category"),
            "version": song.get("version"),
            "image_file": song.get("image_file"),
            "Basic": song.get("lev_bas"),
            "Advanced": song.get("lev_adv"),
            "Expert": song.get("lev_exp"),
            "Master": song.get("lev_mas"),
            "Re:Mas": song.get("lev_remas")
        }
        dx_row = {
            "chart_type": "dx",
            "title": song.get("title"),
            "artist": song.get("artist"),
            "category": song.get("category"),
            "version": song.get("version"),
            "image_file": song.get("image_file"),
            "Basic": song.get("dx_lev_bas"),
            "Advanced": song.get("dx_lev_adv"),
            "Expert": song.get("dx_lev_exp"),
            "Master": song.get("dx_lev_mas"),
            "Re:Mas": song.get("dx_lev_remas")
        }

        if any(std_row[k] for k in ["Basic", "Advanced", "Expert", "Master", "Re:Mas"]):
            split_data.append(std_row)
        if any(dx_row[k] for k in ["Basic", "Advanced", "Expert", "Master", "Re:Mas"]):
            split_data.append(dx_row)

    return split_data