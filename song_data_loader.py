import json

def load_song_data(filepath):
    with open(filepath, "r", encoding="utf-8") as f:
        original_data = json.load(f)

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
