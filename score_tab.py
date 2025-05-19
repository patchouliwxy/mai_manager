from PyQt5.QtWidgets import (
    QWidget, QVBoxLayout, QTableWidget, QTableWidgetItem,
    QPushButton, QFileDialog, QInputDialog, QMessageBox
)
from divingfish_api import fetch_player_scores

class ScoreQueryTab(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        self.sync_btn = QPushButton("📡 从水鱼查分器同步成绩")
        self.sync_btn.clicked.connect(self.sync_from_divingfish)
        layout.addWidget(self.sync_btn)

        self.export_btn = QPushButton("💾 导出为 CSV")
        self.export_btn.clicked.connect(self.export_csv)
        layout.addWidget(self.export_btn)

        self.table = QTableWidget()
        layout.addWidget(self.table)

        self.setLayout(layout)
        self.score_data = []

    def sync_from_divingfish(self):
        token, ok = QInputDialog.getText(self, "导入Token", "请输入 Import-Token：")
        if not ok or not token:
            return
        try:
            result = fetch_player_scores(token)
            self.score_data = result.get("charts", [])  # 这是一个列表
            self.display_scores(self.score_data)
        except Exception as e:
            QMessageBox.critical(self, "同步失败", str(e))

    def display_scores(self, scores):
        if not scores:
            QMessageBox.information(self, "提示", "未获取到任何成绩。")
            return
        headers = ["标题", "难度", "等级", "分数", "评级", "是否 FC", "是否 FS", "是否 AP"]
        self.table.setColumnCount(len(headers))
        self.table.setHorizontalHeaderLabels(headers)
        self.table.setRowCount(len(scores))

        for row, item in enumerate(scores):
            self.table.setItem(row, 0, QTableWidgetItem(item.get("title", "")))
            self.table.setItem(row, 1, QTableWidgetItem(item.get("type", "")))  # Basic/Advanced...
            self.table.setItem(row, 2, QTableWidgetItem(str(item.get("level", ""))))
            self.table.setItem(row, 3, QTableWidgetItem(str(item.get("achievements", ""))))
            self.table.setItem(row, 4, QTableWidgetItem(item.get("rate", "")))
            self.table.setItem(row, 5, QTableWidgetItem(item.get("fc", "-")))
            self.table.setItem(row, 6, QTableWidgetItem(item.get("fs", "-")))
            self.table.setItem(row, 7, QTableWidgetItem(item.get("fullcombo", "-")))

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
            writer.writerow(["标题", "难度", "等级", "分数", "评级", "是否 FC", "是否 FS", "是否 AP"])
            for item in self.score_data:
                writer.writerow([
                    item.get("title", ""),
                    item.get("type", ""),
                    item.get("level", ""),
                    item.get("achievements", ""),
                    item.get("rate", ""),
                    item.get("fc", "-"),
                    item.get("fs", "-"),
                    item.get("fullcombo", "-")
                ])
        QMessageBox.information(self, "成功", "CSV 文件已导出！")
