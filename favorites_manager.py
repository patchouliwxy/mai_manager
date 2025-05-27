# favorites_manager.py
import json
import os
import sys

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

FAV_FILE = resource_path("favorites.json")

def load_favorites():
    if not os.path.exists(FAV_FILE):
        return set()
    with open(FAV_FILE, "r", encoding="utf-8") as f:
        return set(json.load(f))

def save_favorites(fav_set):
    with open(FAV_FILE, "w", encoding="utf-8") as f:
        json.dump(list(fav_set), f, ensure_ascii=False, indent=2)

def toggle_favorite(song_id):
    favs = load_favorites()
    if song_id in favs:
        favs.remove(song_id)
    else:
        favs.add(song_id)
    save_favorites(favs)
    return song_id in favs