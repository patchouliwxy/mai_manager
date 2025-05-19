from PyQt5.QtWidgets import QApplication, QMainWindow, QTabWidget
from song_data_loader import load_song_data
from song_tab import SongSearchTab
from favorite_tab import FavoriteTab
import sys

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("舞萌DX成绩管理系统")
        self.resize(1200, 800)

        self.song_data = load_song_data("maidata.json")
        self.tabs = QTabWidget()

        self.song_tab = SongSearchTab(self.song_data)
        self.favorite_tab = FavoriteTab(self.song_data)

        self.tabs.addTab(self.song_tab, "🎵 乐曲查询")
        self.tabs.addTab(self.favorite_tab, "⭐ 收藏夹")

        self.setCentralWidget(self.tabs)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
