import os
import sqlite3
from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QPixmap, QIcon
from favorites_manager import load_favorites

class SongTableModel(QAbstractTableModel):
    def __init__(self, data, image_dir="images"):
        super().__init__()
        self._original_data = data
        self._data = data
        self.image_dir = image_dir
        self.headers = [
            "收藏", "类型", "封面", "标题", "艺术家", "类别", "版本",
            "Basic", "Advanced", "Expert", "Master", "Re:Mas"
        ]
        self.favorites = load_favorites()

    def rowCount(self, parent=None):
        return len(self._data)

    def columnCount(self, parent=None):
        return len(self.headers)

    def data(self, index, role=Qt.DisplayRole):
        song = self._data[index.row()]
        col = index.column()

        if role == Qt.DisplayRole:
            if col == 0:
                song_id = f"{song['title']}|{song['chart_type']}"
                return "★" if song_id in self.favorites else ""
            elif col == 1:
                return song.get("chart_type", "std")
            elif col == 2:
                return None
            else:
                keys = [
                    "title", "artist", "category", "version",
                    "Basic", "Advanced", "Expert", "Master", "Re:Mas"
                ]
                return str(song.get(keys[col - 3], ""))

        elif role == Qt.DecorationRole and col == 2:
            image_file = song.get("image_file", "")
            path = os.path.join(self.image_dir, image_file)
            if os.path.exists(path):
                pixmap = QPixmap(path).scaled(64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation)
                return QIcon(pixmap)

        return None

    def headerData(self, section, orientation, role):
        if role == Qt.DisplayRole and orientation == Qt.Horizontal:
            return self.headers[section]
        return None

    def filter(self, chart_type=None, versions=None, level=None, categories=None, text="", db_path="maimai_dx.db"):
        query = "SELECT data FROM songs WHERE 1=1"
        params = []
        if chart_type:
            query += " AND json_extract(data, '$.chart_type') = ?"
            params.append(chart_type)
        if versions:
            query += " AND json_extract(data, '$.version') IN ({})".format(
                ",".join("?" for _ in versions)
            )
            params.extend(versions)
        if categories:
            query += " AND json_extract(data, '$.category') IN ({})".format(
                ",".join("?" for _ in categories)
            )
            params.extend(categories)
        if level:
            query += " AND (json_extract(data, '$.Basic') = ? OR json_extract(data, '$.Advanced') = ? OR json_extract(data, '$.Expert') = ? OR json_extract(data, '$.Master') = ? OR json_extract(data, '$.Re:Mas') = ?)"
            params.extend([level] * 5)
        if text:
            query += " AND (json_extract(data, '$.title') LIKE ? OR json_extract(data, '$.artist') LIKE ?)"
            params.extend([f"%{text}%", f"%{text}%"])
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()
        cursor.execute(query, params)
        self._data = [json.loads(row[0]) for row in cursor.fetchall()]
        conn.close()
        self.layoutChanged.emit()

    def get_song(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None