# score_tab.py
from PyQt5 import Qt
from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QInputDialog, QMessageBox, QLineEdit, QLabel
)
from divingfish_api import fetch_player_scores
from song_data_loader import load_song_data
from login_dialog import load_scores  # 导入 load_scores

class ScoreQueryTab(QWidget):
    def __init__(self, song_data=None):
        super().__init__()
        self.song_data = song_data or load_song_data("maidata.json")
        layout = QVBoxLayout()

        # 搜索框
        self.search_box = QLineEdit()
        self.search_box.setPlaceholderText("输入曲目标题或艺术家搜索")
        self.search_box.textChanged.connect(self.apply_search)
        layout.addWidget(self.search_box)

        # 同步按钮
        self.sync_btn = QPushButton("📡 从水鱼查分器同步成绩")
        self.sync_btn.clicked.connect(self.sync_from_divingfish)
        layout.addWidget(self.sync_btn)

        # 导出 CSV 按钮
        self.export_btn = QPushButton("💾 导出为 CSV")
        self.export_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_btn)

        # 用户信息标签
        self.user_info_label = QLabel("用户信息: 未同步")
        layout.addWidget(self.user_info_label)

        # 成绩表格
        self.table = QTableWidget()
        self.table.verticalHeader().setDefaultSectionSize(72)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.score_data = []
        self.raw_data = {}
        self.filtered_data = []

        # 初始化时加载保存的成绩
        saved_data = load_scores()
        if saved_data:
            self.raw_data = saved_data
            self.score_data = saved_data.get("records", [])
            self.filtered_data = self.score_data
            self.user_info_label.setText(
                f"用户信息: {self.raw_data.get('nickname', '未知')} "
                f"(Rating: {self.raw_data.get('rating', 0)})"
            )
            self.display_scores(self.filtered_data)

    def sync_from_divingfish(self):
        token, ok = QInputDialog.getText(self, "导入Token", "请输入 Import-Token：")
        if not ok or not token:
            QMessageBox.warning(self, "警告", "请输入有效的 Token。")
            return
        try:
            result = fetch_player_scores(token)
            self.raw_data = result
            self.score_data = result.get("records", [])
            self.filtered_data = self.score_data
            self.user_info_label.setText(
                f"用户信息: {self.raw_data.get('nickname', '未知')} "
                f"(Rating: {self.raw_data.get('rating', 0)})"
            )
            self.display_scores(self.filtered_data)
        except Exception as e:
            error_msg = str(e)
            if "导入token有误" in error_msg:
                QMessageBox.critical(self, "同步失败", "Import-Token 无效，请检查或重新生成。")
            elif "已设置隐私或未同意用户协议" in error_msg:
                QMessageBox.critical(self, "同步失败", "用户已设置隐私或未同意用户协议，请在查分器官网检查设置。")
            else:
                QMessageBox.critical(self, "同步失败", str(e))

    def apply_search(self):
        keyword = self.search_box.text().strip().lower()
        if not keyword:
            self.filtered_data = self.score_data
        else:
            self.filtered_data = [
                item for item in self.score_data
                if keyword in item.get("title", "").lower() or
                   keyword in self.get_artist(item.get("title", ""), item.get("type", "")).lower()
            ]
        self.display_scores(self.filtered_data)

    def get_artist(self, title, chart_type):
        for song in self.song_data:
            if song.get("title") == title and song.get("chart_type") == chart_type.lower():
                return song.get("artist", "")
        return ""

    def display_scores(self, scores):
        if not scores:
            QMessageBox.information(self, "提示", "未获取到任何成绩。")
            return
        headers = [
            "谱面类型", "歌曲标题", "难度索引", "等级", "定数",
            "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(scores))
        self.table.setColumnWidth(0, 60)  # 谱面类型
        self.table.setColumnWidth(2, 80)  # 难度索引
        self.table.setColumnWidth(3, 60)  # 等级
        self.table.setColumnWidth(4, 60)  # 定数
        self.table.setColumnWidth(5, 100) # 成绩百分比
        self.table.setColumnWidth(9, 100)  # 单曲 Rating
        self.table.setColumnWidth(10, 100) # DX 分数

        for row, item in enumerate(scores):
            self.table.setItem(row, 0, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("title", "")))
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("level_index", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(item.get("level", "")))
            self.table.setItem(row, 4, QTableWidgetItem(str(item.get("ds", ""))))
            self.table.setItem(row, 5, QTableWidgetItem(str(item.get("achievements", ""))))
            self.table.setItem(row, 6, QTableWidgetItem(item.get("rate", "")))
            self.table.setItem(row, 7, QTableWidgetItem(item.get("fc", "-")))
            self.table.setItem(row, 8, QTableWidgetItem(item.get("fs", "-")))
            self.table.setItem(row, 9, QTableWidgetItem(str(item.get("ra", ""))))
            self.table.setItem(row, 10, QTableWidgetItem(str(item.get("dxScore", ""))))

    def export_csv(self):
        if not self.score_data:
            QMessageBox.information(self, "提示", "请先同步数据。")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "导出为 CSV", "scores.csv", "CSV 文件 (*.csv)")
        if not file_path:
            return

        import csv
        with open(file_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["用户名", self.raw_data.get("username", "")])
            writer.writerow(["昵称", self.raw_data.get("nickname", "")])
            writer.writerow(["段位", self.raw_data.get("additional_rating", 0)])
            writer.writerow(["牌子", self.raw_data.get("plate", "")])
            writer.writerow(["总 Rating", self.raw_data.get("rating", 0)])
            writer.writerow([])
            writer.writerow([
                "谱面类型", "歌曲标题", "难度索引", "等级", "定数",
                "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数"
            ])
            for item in self.filtered_data:
                writer.writerow([
                    item.get("type", ""),
                    item.get("title", ""),
                    item.get("level_index", ""),
                    item.get("level", ""),
                    item.get("ds", ""),
                    item.get("achievements", ""),
                    item.get("rate", ""),
                    item.get("fc", "-"),
                    item.get("fs", "-"),
                    item.get("ra", ""),
                    item.get("dxScore", "")
                ])
        QMessageBox.information(self, "成功", "CSV 文件已导出！")