# login_dialog.py
import json
import os
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from divingfish_api import fetch_player_scores

CONFIG_PATH = "config.json"
SCORES_PATH = "scores.json"  # 新增成绩保存文件

def save_token(token):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"import_token": token}, f)

def load_token():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("import_token")
    return None

def save_scores(scores_data):
    with open(SCORES_PATH, "w", encoding="utf-8") as f:
        json.dump(scores_data, f, ensure_ascii=False, indent=2)

def load_scores():
    if os.path.exists(SCORES_PATH):
        with open(SCORES_PATH, "r", encoding="utf-8") as f:
            return json.load(f)
    return None

class LoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("登录水鱼查分器")
        self.resize(300, 150)
        self.parent = parent  # 保存父窗口引用

        layout = QVBoxLayout()
        layout.addWidget(QLabel("请输入 Import-Token："))
        layout.addWidget(
            QLabel("请在 https://www.diving-fish.com/maimaidx/prober/ 的‘编辑个人资料’中生成 Import-Token"))
        self.token_input = QLineEdit()

        existing_token = load_token()
        if existing_token:
            self.token_input.setText(existing_token)
            layout.addWidget(QLabel("已检测到保存的 Token。"))

        layout.addWidget(self.token_input)

        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.accept_and_save)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def accept_and_save(self):
        token = self.get_token()
        if not token:
            QMessageBox.warning(self, "警告", "请输入有效的 Token。")
            return
        try:
            # 验证 Token 并获取成绩
            scores_data = fetch_player_scores(token)
            save_token(token)
            save_scores(scores_data)  # 保存成绩
            # 自动触发成绩查询页面的同步
            if hasattr(self.parent, 'score_tab'):
                self.parent.score_tab.raw_data = scores_data
                self.parent.score_tab.score_data = scores_data.get("records", [])
                self.parent.score_tab.filtered_data = self.parent.score_tab.score_data
                self.parent.score_tab.user_info_label.setText(
                    f"用户信息: {scores_data.get('nickname', '未知')} "
                    f"(Rating: {scores_data.get('rating', 0)})"
                )
                self.parent.score_tab.display_scores(self.parent.score_tab.filtered_data)
            QMessageBox.information(self, "成功", "Token 验证通过，成绩已同步并保存！")
            self.accept()
        except Exception as e:
            QMessageBox.critical(self, "错误", f"Token 验证失败：{str(e)}")

    def get_token(self):
        return self.token_input.text().strip()