from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QTabWidget, QWidget, QHBoxLayout,
    QVBoxLayout, QLabel, QPushButton, QSpacerItem, QSizePolicy
)
from song_data_loader import load_song_data
from song_tab import SongSearchTab
from favorite_tab import FavoriteTab
from score_tab import ScoreQueryTab
from login_dialog import LoginDialog

import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("舞萌DX成绩管理系统")
        self.resize(1200, 800)

        # 导入数据
        self.song_data = load_song_data("maidata.json")

        # ---------- 上方工具栏 ----------
        top_bar = QWidget()
        top_layout = QHBoxLayout()
        top_layout.setContentsMargins(10, 5, 10, 5)

        title = QLabel("🎼 舞萌DX 成绩管理系统")
        title.setStyleSheet("font-size: 18px; font-weight: bold;")
        top_layout.addWidget(title)

        top_layout.addSpacerItem(QSpacerItem(40, 20, QSizePolicy.Expanding, QSizePolicy.Minimum))

        # 收藏夹按钮
        fav_btn = QPushButton("收藏夹")
        fav_btn.clicked.connect(self.goto_favorite_tab)
        top_layout.addWidget(fav_btn)

        # 登录按钮
        login_btn = QPushButton("登录")
        login_btn.clicked.connect(self.open_login)
        top_layout.addWidget(login_btn)

        top_bar.setLayout(top_layout)

        # ---------- 主体 Tab ----------
        self.tabs = QTabWidget()
        self.song_tab = SongSearchTab(self.song_data)
        self.favorite_tab = FavoriteTab(self.song_data)
        self.score_tab = ScoreQueryTab()

        self.tabs.addTab(self.song_tab, "🎵 乐曲查询")
        self.tabs.addTab(self.favorite_tab, "⭐ 收藏夹")
        self.tabs.addTab(self.score_tab, "📊 成绩查询")

        # ---------- 主体布局 ----------
        central_widget = QWidget()
        central_layout = QVBoxLayout()
        central_layout.setContentsMargins(0, 0, 0, 0)
        central_layout.addWidget(top_bar)
        central_layout.addWidget(self.tabs)

        central_widget.setLayout(central_layout)
        self.setCentralWidget(central_widget)

    def open_login(self):
        dialog = LoginDialog(self)
        if dialog.exec_():
            token = dialog.get_token()
            print(f"登录成功：{token}")

    def goto_favorite_tab(self):
        self.tabs.setCurrentWidget(self.favorite_tab)

# ---------- 启动 ----------
if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
