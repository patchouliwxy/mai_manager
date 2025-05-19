from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QMessageBox, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import QSize
from song_model import SongTableModel
from favorites_manager import toggle_favorite, load_favorites
from filter_dialog import FilterDialog

class SongSearchTab(QWidget):
    def __init__(self, song_data):
        super().__init__()
        self.full_data = song_data
        self.model = SongTableModel(song_data)

        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入曲目标题或艺术家搜索")
        self.search_box.textChanged.connect(self.apply_filters)

        self.table_view = QTableView()
        self.table_view.setModel(self.model)
        self.table_view.setIconSize(QSize(64, 64))
        self.table_view.verticalHeader().setDefaultSectionSize(72)
        self.table_view.setColumnWidth(0, 50)
        self.table_view.setColumnWidth(1, 50)
        self.table_view.setColumnWidth(2, 80)
        self.table_view.setSortingEnabled(True)
        self.table_view.doubleClicked.connect(self.show_song_detail)

        # 筛选设置按钮
        self.chart_type = None
        self.selected_versions = None
        self.selected_categories = None
        self.selected_level = None

        filter_btn = QPushButton("筛选设置")
        filter_btn.clicked.connect(self.open_filter_dialog)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(filter_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

    def open_filter_dialog(self):
        versions = sorted(set(s["version"] for s in self.full_data))
        categories = sorted(set(s["category"] for s in self.full_data))

        dialog = FilterDialog(versions, categories, self)
        if dialog.exec_():
            self.chart_type, self.selected_versions, self.selected_level, self.selected_categories = dialog.get_filters()
            self.apply_filters()

    def apply_filters(self):
        keyword = self.search_box.text().strip()
        self.model.filter(
            chart_type=self.chart_type,
            versions=self.selected_versions,
            level=self.selected_level,
            categories=self.selected_categories,
            text=keyword
        )

    def show_song_detail(self, index):
        row = index.row()
        song = self.model.get_song(row)
        if not song:
            return

        song_id = f"{song['title']}|{song['chart_type']}"
        is_favorited = song_id in self.model.favorites

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
        fav_btn = msg.addButton("★ 收藏" if not is_favorited else "☆ 取消收藏", QMessageBox.ActionRole)
        msg.addButton("关闭", QMessageBox.RejectRole)
        msg.exec_()

        if msg.clickedButton() == fav_btn:
            new_state = toggle_favorite(song_id)
            self.model.favorites = load_favorites()
            self.model.layoutChanged.emit()
