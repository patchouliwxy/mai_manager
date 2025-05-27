from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QMessageBox, QLabel
)
from divingfish_api import fetch_player_scores
from song_data_loader import load_song_data
from login_dialog import load_scores, LoginDialog
import requests


class Best50Tab(QWidget):
    def __init__(self, song_data=None):
        super().__init__()
        self.song_data = song_data or load_song_data("maidata.json")
        layout = QVBoxLayout()

        self.sync_btn = QPushButton("📡 同步Best50成绩")
        self.sync_btn.clicked.connect(self.sync_from_divingfish)
        layout.addWidget(self.sync_btn)

        self.export_btn = QPushButton("💾 导出为 CSV")
        self.export_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_btn)

        self.user_info_label = QLabel("用户信息: 未同步")
        layout.addWidget(self.user_info_label)

        self.table = QTableWidget()
        self.table.verticalHeader().setDefaultSectionSize(72)
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.score_data = []
        self.raw_data = {}
        self.filtered_data = []

        saved_data = load_scores()
        if saved_data:
            self.raw_data = saved_data
            self.score_data = self.get_best50_data(saved_data)
            self.filtered_data = self.score_data
            self.user_info_label.setText(
                f"用户信息: {self.raw_data.get('nickname', '未知')} "
                f"(Rating: {self.raw_data.get('rating', 0)})"
            )
            self.display_scores(self.filtered_data)

    def get_best50_data(self, raw_data):
        """提取Best50数据：旧版本前35首 + 舞萌2024前15首"""
        records = raw_data.get("records", [])

        # 获取所有版本信息
        versions = set(s.get("version") for s in self.song_data)
        current_version = "舞萌DX 2024"  # 当前版本
        old_versions = [v for v in versions if v != current_version]

        # 分离旧版本和新版本的常规谱面
        old_records = [r for r in records if
                       self.get_song_version(r.get("title", ""), r.get("type", "")) in old_versions]
        new_records = [r for r in records if
                       self.get_song_version(r.get("title", ""), r.get("type", "")) == current_version]

        # 按单曲Rating（ra）降序排序，分别取前35和前15
        old_records_sorted = sorted(old_records, key=lambda x: x.get("ra", 0), reverse=True)[:35]
        new_records_sorted = sorted(new_records, key=lambda x: x.get("ra", 0), reverse=True)[:15]

        # 返回扁平化数据，包含分隔行标记
        return {
            "old": old_records_sorted,
            "new": new_records_sorted
        }

    def get_song_version(self, title, chart_type):
        """根据歌曲标题和谱面类型获取版本"""
        for song in self.song_data:
            if song.get("title") == title and song.get("chart_type") == chart_type.lower():
                return song.get("version", "")
        return ""

    def sync_from_divingfish(self):
        dialog = LoginDialog(self)
        if dialog.exec_():
            try:
                username = dialog.username_input.text().strip()
                password = dialog.password_input.text().strip()
                if not username or not password:
                    QMessageBox.warning(self, "警告", "请输入用户名和密码。")
                    return
                session = requests.Session()
                login(username, password, session)
                result = fetch_player_scores(session)
                self.raw_data = result
                self.score_data = self.get_best50_data(result)
                self.filtered_data = self.score_data
                self.user_info_label.setText(
                    f"用户信息: {self.raw_data.get('nickname', '未知')} "
                    f"(Rating: {self.raw_data.get('rating', 0)})"
                )
                self.display_scores(self.filtered_data)
            except Exception as e:
                error_msg = str(e)
                if "登录失败" in error_msg:
                    QMessageBox.critical(self, "同步失败", "用户名或密码错误，请检查。")
                else:
                    QMessageBox.critical(self, "同步失败", error_msg)

    def display_scores(self, score_data):
        if not score_data or (not score_data["old"] and not score_data["new"]):
            QMessageBox.information(self, "提示", "未获取到任何Best50成绩。")
            return

        headers = [
            "谱面类型", "歌曲标题", "难度索引", "等级", "定数",
            "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数", "版本"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)


        self.table.setRowCount(50)

        # 设置列宽
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 60)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(9, 100)
        self.table.setColumnWidth(10, 100)
        self.table.setColumnWidth(11, 100)

        # 显示旧版本前35首（1-35行）
        for row, item in enumerate(score_data["old"]):
            if row < 35:
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
                self.table.setItem(row, 11,
                                   QTableWidgetItem(self.get_song_version(item.get("title", ""), item.get("type", ""))))



        # 显示舞萌2024前15首（36-50行，表格索引35-49）
        for row, item in enumerate(score_data["new"]):
            if row < 15:
                table_row = 35 + row
                self.table.setItem(table_row, 0, QTableWidgetItem(item.get("type", "")))
                self.table.setItem(table_row, 1, QTableWidgetItem(item.get("title", "")))
                self.table.setItem(table_row, 2, QTableWidgetItem(str(item.get("level_index", ""))))
                self.table.setItem(table_row, 3, QTableWidgetItem(item.get("level", "")))
                self.table.setItem(table_row, 4, QTableWidgetItem(str(item.get("ds", ""))))
                self.table.setItem(table_row, 5, QTableWidgetItem(str(item.get("achievements", ""))))
                self.table.setItem(table_row, 6, QTableWidgetItem(item.get("rate", "")))
                self.table.setItem(table_row, 7, QTableWidgetItem(item.get("fc", "-")))
                self.table.setItem(table_row, 8, QTableWidgetItem(item.get("fs", "-")))
                self.table.setItem(table_row, 9, QTableWidgetItem(str(item.get("ra", ""))))
                self.table.setItem(table_row, 10, QTableWidgetItem(str(item.get("dxScore", ""))))
                self.table.setItem(table_row, 11,
                                   QTableWidgetItem(self.get_song_version(item.get("title", ""), item.get("type", ""))))

    def export_csv(self):
        if not self.score_data or (not self.score_data["old"] and not self.score_data["new"]):
            QMessageBox.information(self, "提示", "请先同步Best50数据。")
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "导出为 CSV", "best50.csv", "CSV 文件 (*.csv)")
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
                "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数", "版本"
            ])

            # 旧版本前35首
            writer.writerow(["旧版本（前35首）"])
            for item in self.score_data["old"][:35]:
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
                    item.get("dxScore", ""),
                    self.get_song_version(item.get("title", ""), item.get("type", ""))
                ])

            # 分隔线
            writer.writerow(["--- 分隔线 ---"])

            # 舞萌2024前15首
            writer.writerow(["舞萌2024（前15首）"])
            for item in self.score_data["new"][:15]:
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
                    item.get("dxScore", ""),
                    self.get_song_version(item.get("title", ""), item.get("type", ""))
                ])

        QMessageBox.information(self, "成功", "Best50 CSV 文件已导出！")