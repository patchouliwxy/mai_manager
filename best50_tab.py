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
        records = raw_data.get("records", [])

        # 定义当前版本（最新版本）
        current_version = "舞萌DX 2024"

        # 分离旧版本和新版本的记录
        old_records = []
        new_records = []

        for record in records:
            song_version = self.get_song_version(record.get("title", ""), record.get("type", ""))

            # 如果找到了版本信息
            if song_version:
                if song_version == current_version:
                    new_records.append(record)
                else:
                    old_records.append(record)
            else:
                # 如果没有找到版本信息，默认归类为旧版本
                old_records.append(record)

        # 按单曲Rating（ra）降序排序，分别取前35和前15
        old_records_sorted = sorted(old_records, key=lambda x: x.get("ra", 0), reverse=True)[:35]
        new_records_sorted = sorted(new_records, key=lambda x: x.get("ra", 0), reverse=True)[:15]

        return {
            "old": old_records_sorted,
            "new": new_records_sorted
        }

    def get_song_version(self, title, chart_type):
        """根据歌曲标题和谱面类型获取版本"""
        # 遍历所有歌曲数据寻找匹配的歌曲
        for song in self.song_data:
            if (song.get("title", "").strip() == title.strip() and
                    song.get("chart_type", "").lower() == chart_type.lower()):
                return song.get("version", "")

        # 如果没有找到精确匹配，尝试模糊匹配（处理可能的标题差异）
        for song in self.song_data:
            if (title.strip().lower() in song.get("title", "").strip().lower() or
                    song.get("title", "").strip().lower() in title.strip().lower()):
                if song.get("chart_type", "").lower() == chart_type.lower():
                    return song.get("version", "")

        # 如果仍然没有找到，返回空字符串
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
            "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数"
        ]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)

        # 计算实际需要的行数
        total_rows = len(score_data["old"]) + len(score_data["new"])
        self.table.setRowCount(max(50, total_rows))  # 至少50行，或者根据实际数据调整

        # 设置列宽
        self.table.setColumnWidth(0, 60)
        self.table.setColumnWidth(2, 80)
        self.table.setColumnWidth(3, 60)
        self.table.setColumnWidth(4, 60)
        self.table.setColumnWidth(5, 100)
        self.table.setColumnWidth(9, 100)
        self.table.setColumnWidth(10, 100)

        current_row = 0

        # 显示旧版本前35首
        for item in score_data["old"]:
            if current_row >= self.table.rowCount():
                break

            self.table.setItem(current_row, 0, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(current_row, 1, QTableWidgetItem(item.get("title", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(str(item.get("level_index", ""))))
            self.table.setItem(current_row, 3, QTableWidgetItem(item.get("level", "")))
            self.table.setItem(current_row, 4, QTableWidgetItem(str(item.get("ds", ""))))
            self.table.setItem(current_row, 5, QTableWidgetItem(str(item.get("achievements", ""))))
            self.table.setItem(current_row, 6, QTableWidgetItem(item.get("rate", "")))
            self.table.setItem(current_row, 7, QTableWidgetItem(item.get("fc", "-")))
            self.table.setItem(current_row, 8, QTableWidgetItem(item.get("fs", "-")))
            self.table.setItem(current_row, 9, QTableWidgetItem(str(item.get("ra", ""))))
            self.table.setItem(current_row, 10, QTableWidgetItem(str(item.get("dxScore", ""))))
            version = self.get_song_version(item.get("title", ""), item.get("type", ""))
            current_row += 1

        # 显示舞萌2024前15首
        for item in score_data["new"]:
            if current_row >= self.table.rowCount():
                break

            self.table.setItem(current_row, 0, QTableWidgetItem(item.get("type", "")))
            self.table.setItem(current_row, 1, QTableWidgetItem(item.get("title", "")))
            self.table.setItem(current_row, 2, QTableWidgetItem(str(item.get("level_index", ""))))
            self.table.setItem(current_row, 3, QTableWidgetItem(item.get("level", "")))
            self.table.setItem(current_row, 4, QTableWidgetItem(str(item.get("ds", ""))))
            self.table.setItem(current_row, 5, QTableWidgetItem(str(item.get("achievements", ""))))
            self.table.setItem(current_row, 6, QTableWidgetItem(item.get("rate", "")))
            self.table.setItem(current_row, 7, QTableWidgetItem(item.get("fc", "-")))
            self.table.setItem(current_row, 8, QTableWidgetItem(item.get("fs", "-")))
            self.table.setItem(current_row, 9, QTableWidgetItem(str(item.get("ra", ""))))
            self.table.setItem(current_row, 10, QTableWidgetItem(str(item.get("dxScore", ""))))
            version = self.get_song_version(item.get("title", ""), item.get("type", ""))
            current_row += 1

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
                "成绩百分比", "评级", "FC", "FS", "单曲 Rating", "DX 分数"
            ])

            # 旧版本前35首
            writer.writerow(["旧版本（前35首）"])
            for item in self.score_data["old"]:
                version = self.get_song_version(item.get("title", ""), item.get("type", ""))
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
                ])

            # 分隔线
            writer.writerow(["--- 分隔线 ---"])

            # 舞萌2024前15首
            writer.writerow(["舞萌2024（前15首）"])
            for item in self.score_data["new"]:
                version = self.get_song_version(item.get("title", ""), item.get("type", ""))
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
                ])

        QMessageBox.information(self, "成功", "Best50 CSV 文件已导出！")