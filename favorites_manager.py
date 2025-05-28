import sqlite3
import json

def load_favorites(user_id="default", db_path="maimai_dx.db"):
    """从 SQLite 加载收藏数据"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS favorites (user_id TEXT, song_id TEXT, PRIMARY KEY (user_id, song_id))")
    cursor.execute("SELECT song_id FROM favorites WHERE user_id = ?", (user_id,))
    favs = set(row[0] for row in cursor.fetchall())
    conn.close()
    return favs

def save_favorites(fav_set, user_id="default", db_path="maimai_dx.db"):
    """保存收藏数据到 SQLite"""
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("CREATE TABLE IF NOT EXISTS favorites (user_id TEXT, song_id TEXT, PRIMARY KEY (user_id, song_id))")
    cursor.execute("DELETE FROM favorites WHERE user_id = ?", (user_id,))
    for fid in fav_set:
        cursor.execute("INSERT INTO favorites (user_id, song_id) VALUES (?, ?)", (user_id, fid))
    conn.commit()
    conn.close()

def toggle_favorite(song_id, user_id="default", db_path="maimai_dx.db"):
    """切换收藏状态"""
    favs = load_favorites(user_id, db_path)
    if song_id in favs:
        favs.remove(song_id)
    else:
        favs.add(song_id)
    save_favorites(favs, user_id, db_path)
    return song_id in favs