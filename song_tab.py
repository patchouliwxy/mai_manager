from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QLineEdit, QTableView, QMessageBox, QPushButton, QHBoxLayout
)
from PyQt5.QtCore import QSize
from song_model import SongTableModel
from favorites_manager import toggle_favorite, load_favorites
from filter_dialog import FilterDialog
from add_song_dialog import AddSongDialog
from song_data_loader import load_song_data, save_song_data, delete_song_data

class SongSearchTab(QWidget):
    def __init__(self, song_data, parent=None):
        super().__init__(parent)
        self.full_data = song_data
        self.model = SongTableModel(song_data)
        self.parent = parent

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

        # 新增添加和删除按钮
        self.add_song_btn = QPushButton("添加歌曲")
        self.add_song_btn.setObjectName("add_song_btn")
        self.add_song_btn.clicked.connect(self.add_song)
        self.delete_song_btn = QPushButton("删除歌曲")
        self.delete_song_btn.setObjectName("delete_song_btn")
        self.delete_song_btn.clicked.connect(self.delete_selected_song)

        top_layout = QHBoxLayout()
        top_layout.addWidget(self.search_box)
        top_layout.addWidget(filter_btn)
        top_layout.addWidget(self.add_song_btn)
        top_layout.addWidget(self.delete_song_btn)

        layout = QVBoxLayout()
        layout.addLayout(top_layout)
        layout.addWidget(self.table_view)
        self.setLayout(layout)

        # 初始化按钮状态
        self.refresh_data()

    def refresh_data(self):
        """刷新歌曲数据"""
        try:
            self.full_data = load_song_data("maimai_dx.db")
            self.model._original_data = self.full_data
            self.model._data = self.full_data
            self.model.layoutChanged.emit()
            # 更新按钮状态
            is_admin = getattr(self.parent, 'is_admin_logged_in', False)
            self.add_song_btn.setEnabled(is_admin)
            self.delete_song_btn.setEnabled(is_admin)
        except Exception as e:
            QMessageBox.critical(self, "错误", f"刷新数据失败：{str(e)}")

    def open_filter_dialog(self):
        try:
            versions = sorted(set(s["version"] for s in self.full_data))
            categories = sorted(set(s["category"] for s in self.full_data))
            dialog = FilterDialog(versions, categories, self)
            if dialog.exec_():
                self.chart_type, self.selected_versions, self.selected_level, self.selected_categories = dialog.get_filters()
                self.apply_filters()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"打开筛选对话框失败：{str(e)}")

    def apply_filters(self):
        try:
            keyword = self.search_box.text().strip()
            self.model.filter(
                chart_type=self.chart_type,
                versions=self.selected_versions,
                level=self.selected_level,
                categories=self.selected_categories,
                text=keyword
            )
        except Exception as e:
            QMessageBox.critical(self, "错误", f"应用筛选失败：{str(e)}")

    def add_song(self):
        """添加新歌曲"""
        if not getattr(self.parent, 'is_admin_logged_in', False):
            QMessageBox.warning(self, "无权限", "需要管理员权限才能添加歌曲！")
            return

        try:
            dialog = AddSongDialog(self)
            if dialog.exec_():
                song_data = dialog.get_song_data()
                if not song_data["title"]:
                    QMessageBox.warning(self, "错误", "歌曲标题不能为空！")
                    return
                save_song_data(song_data)
                self.refresh_data()
                QMessageBox.information(self, "成功", "歌曲已添加！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"添加歌曲失败：{str(e)}")

    def delete_selected_song(self):
        """删除选中的歌曲"""
        if not getattr(self.parent, 'is_admin_logged_in', False):
            QMessageBox.warning(self, "无权限", "需要管理员权限才能删除歌曲！")
            return

        try:
            selected = self.table_view.selectionModel().selectedRows()
            if not selected:
                QMessageBox.warning(self, "错误", "请先选择一首歌曲！")
                return

            row = selected[0].row()
            song = self.model.get_song(row)
            if not song:
                return

            reply = QMessageBox.question(
                self, "确认删除",
                f"确定要删除歌曲 '{song['title']}' ({song['chart_type'].upper()}) 吗？",
                QMessageBox.Yes | QMessageBox.No, QMessageBox.No
            )
            if reply == QMessageBox.Yes:
                delete_song_data(song["title"], song["chart_type"])
                self.refresh_data()
                QMessageBox.information(self, "成功", "歌曲已删除！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"删除歌曲失败：{str(e)}")

    def show_song_detail(self, index):
        try:
            row = index.row()
            song = self.model.get_song(row)
            if not song:
                return

            song_id = f"{song['title']}|{song['chart_type']}"
            is_favorited = song_id in self.model.favorites

            best50_score = self.get_best50_score(song['title'], song['chart_type'])

            detail = f"""🎵 {song.get('title', '')}
👤 艺术家: {song.get('artist', '')}
📂 类别: {song.get('category', '')}
🕹️ 版本: {song.get('version', '')}
🎼 谱面类型: {song.get('chart_type').upper()}

难度：
Basic: {song.get('Basic', '-')}, Advanced: {song.get('Advanced', '-')},
Expert: {song.get('Expert', '-')}, Master: {song.get('Master', '-')},
Re:Mas: {song.get('Re:Mas', '-')}

Best50 成绩：
{self.format_best50_score(best50_score) if best50_score else '未在 Best50 列表中'}
"""

            msg = QMessageBox(self)
            msg.setWindowTitle("乐曲详情")
            msg.setText(detail)
            fav_btn = msg.addButton("★ 收藏" if not is_favorited else "☆ 取消收藏", QMessageBox.ActionRole)
            delete_btn = msg.addButton("删除歌曲", QMessageBox.ActionRole) if getattr(self.parent, 'is_admin_logged_in', False) else None
            msg.addButton("关闭", QMessageBox.RejectRole)
            msg.exec_()

            if msg.clickedButton() == fav_btn:
                new_state = toggle_favorite(song_id)
                self.model.favorites = load_favorites()
                self.model.layoutChanged.emit()
                if self.parent:
                    self.parent.refresh_favorite_tab()
            elif msg.clickedButton() == delete_btn and getattr(self.parent, 'is_admin_logged_in', False):
                reply = QMessageBox.question(
                    self, "确认删除",
                    f"确定要删除歌曲 '{song['title']}' ({song['chart_type'].upper()}) 吗？",
                    QMessageBox.Yes | QMessageBox.No, QMessageBox.No
                )
                if reply == QMessageBox.Yes:
                    delete_song_data(song["title"], song["chart_type"])
                    self.refresh_data()
                    QMessageBox.information(self, "成功", "歌曲已删除！")
        except Exception as e:
            QMessageBox.critical(self, "错误", f"显示乐曲详情失败：{str(e)}")

    def get_best50_score(self, title, chart_type):
        """从 Best50Tab 获取歌曲的 Best50 成绩"""
        try:
            if hasattr(self.parent, 'best50_tab') and self.parent.best50_tab.score_data:
                for record in self.parent.best50_tab.score_data.get('old', []) + self.parent.best50_tab.score_data.get('new', []):
                    if record.get('title') == title and record.get('type') == chart_type:
                        return record
            return None
        except Exception as e:
            return None

    def format_best50_score(self, score):
        """格式化 Best50 成绩显示"""
        try:
            return f"""等级: {score.get('level', '-')}, 定数: {score.get('ds', '-')},
成绩百分比: {score.get('achievements', '-')}, 评级: {score.get('rate', '-')},
FC: {score.get('fc', '-')}, FS: {score.get('fs', '-')},
单曲 Rating: {score.get('ra', '-')}, DX 分数: {score.get('dxScore', '-')}"""
        except Exception as e:
            return "成绩格式化失败"