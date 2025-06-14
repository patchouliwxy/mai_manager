# favorite_tab.py
from PyQt5.QtWidgets import QWidget, QVBoxLayout, QTableView, QMessageBox
from PyQt5.QtCore import QSize
from song_model import SongTableModel
from favorites_manager import load_favorites, toggle_favorite
import logging  # 添加日志记录

# 设置日志
logging.basicConfig(level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

class FavoriteTab(QWidget):
    def __init__(self, full_data):
        super().__init__()
        self.full_data = full_data
        self.model = SongTableModel(self.get_favorited_data())

        self.table = QTableView()
        self.table.setModel(self.model)
        self.table.setIconSize(QSize(64, 64))
        self.table.verticalHeader().setDefaultSectionSize(72)
        self.table.setColumnWidth(0, 50)
        self.table.setColumnWidth(1, 50)
        self.table.setColumnWidth(2, 80)
        self.table.setSortingEnabled(True)
        self.table.doubleClicked.connect(self.show_song_detail)

        layout = QVBoxLayout()
        layout.addWidget(self.table)
        self.setLayout(layout)

    def get_favorited_data(self):
        fav_ids = load_favorites()
        return [s for s in self.full_data if f"{s['title']}|{s['chart_type']}" in fav_ids]

    def refresh(self):
        self.model._original_data = self.get_favorited_data()
        self.model._data = self.model._original_data
        self.model.layoutChanged.emit()

    def show_song_detail(self, index):
        try:
            row = index.row()
            song = self.model.get_song(row)
            if not song:
                logging.warning(f"No song found at row {row}")
                QMessageBox.warning(self, "错误", "无法获取乐曲信息")
                return

            song_id = f"{song['title']}|{song['chart_type']}"
            is_favorited = song_id in self.model.favorites
            logging.debug(f"Showing details for song_id: {song_id}, favorited: {is_favorited}")

            detail = f"""🎵 {song.get('title', '')}
👤 艺术家: {song.get('artist', '')}
📂 类别: {song.get('category', '')}
🕹️ 版本: {song.get('version', '')}
🎼 谱面类型: {song.get('chart_type').upper()}

难度：
Basic: {song.get('Basic', '-')}, Advanced: {song.get('Advanced', '-')},
Expert: {song.get('Expert', '-')}, Master: {song.get('Master', '-')},
Re:Mas: {song.get('Re:Mas', '-')}
"""

            msg = QMessageBox(self)
            msg.setWindowTitle("乐曲详情")
            msg.setText(detail)
            fav_btn = msg.addButton("☆ 取消收藏", QMessageBox.ActionRole)
            msg.addButton("关闭", QMessageBox.RejectRole)
            msg.exec_()

            if msg.clickedButton() == fav_btn:
                logging.debug(f"Toggling favorite for song_id: {song_id}")
                toggle_favorite(song_id)
                self.refresh()
                logging.info(f"Favorite toggled and refreshed for song_id: {song_id}")

        except Exception as e:
            logging.error(f"Error in show_song_detail: {str(e)}", exc_info=True)
            QMessageBox.critical(self, "错误", f"显示乐曲详情时出错：{str(e)}")