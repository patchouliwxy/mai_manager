from PyQt5.QtCore import QAbstractTableModel, Qt
from PyQt5.QtGui import QPixmap, QIcon
import os
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

    def filter(self, chart_type=None, versions=None, level=None, categories=None, text=""):
        text = text.lower()
        self._data = []
        for s in self._original_data:
            if chart_type and s.get("chart_type") != chart_type:
                continue
            if versions and s.get("version") not in versions:
                continue
            if categories and s.get("category") not in categories:
                continue
            if level:
                levels = [s.get(k, "") for k in ["Basic", "Advanced", "Expert", "Master", "Re:Mas"]]
                if level not in levels:
                    continue
            if text and text not in s.get("title", "").lower() and text not in s.get("artist", "").lower():
                continue
            self._data.append(s)
        self.layoutChanged.emit()

    def get_song(self, row):
        if 0 <= row < len(self._data):
            return self._data[row]
        return None
