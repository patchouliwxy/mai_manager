# login_dialog.py
import json
import os
import requests
import sys
from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox
from divingfish_api import fetch_player_scores, login

def resource_path(relative_path):
    if hasattr(sys, '_MEIPASS'):
        return os.path.join(sys._MEIPASS, relative_path)
    return os.path.join(os.path.abspath("."), relative_path)

CONFIG_PATH = resource_path("config.json")
SCORES_PATH = resource_path("scores.json")

def save_token(token):
    with open(CONFIG_PATH, "w", encoding="utf-8") as f:
        json.dump({"jwt_token": token}, f)

def load_token():
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "r", encoding="utf-8") as f:
            data = json.load(f)
            return data.get("jwt_token")
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
        self.resize(300, 200)
        self.parent = parent

        layout = QVBoxLayout()
        layout.addWidget(QLabel("请输入用户名和密码："))
        layout.addWidget(
            QLabel("请在 https://www.diving-fish.com/maimaidx/prober/ 注册并获取用户名和密码"))

        layout.addWidget(QLabel("用户名："))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("密码："))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.accept_and_save)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def accept_and_save(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()
        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码。")
            return
        try:
            session = requests.Session()
            token = login(username, password, session)
            scores_data = fetch_player_scores(session)
            save_token(token)
            save_scores(scores_data)
            if hasattr(self.parent, 'score_tab'):
                self.parent.score_tab.raw_data = scores_data
                self.parent.score_tab.score_data = scores_data.get("records", [])
                self.parent.score_tab.filtered_data = self.parent.score_tab.score_data
                self.parent.score_tab.user_info_label.setText(
                    f"用户信息: {scores_data.get('nickname', '未知')} "
                    f"(Rating: {scores_data.get('rating', 0)})"
                )
                self.parent.score_tab.display_scores(self.parent.score_tab.filtered_data)
            if hasattr(self.parent, 'best50_tab'):
                self.parent.best50_tab.raw_data = scores_data
                self.parent.best50_tab.score_data = self.parent.best50_tab.get_best50_data(scores_data)
                self.parent.best50_tab.filtered_data = self.parent.best50_tab.score_data
                self.parent.best50_tab.user_info_label.setText(
                    f"用户信息: {scores_data.get('nickname', '未知')} "
                    f"(Rating: {scores_data.get('rating', 0)})"
                )
                self.parent.best50_tab.display_scores(self.parent.best50_tab.filtered_data)
            QMessageBox.information(self, "成功", "登录成功，成绩已同步并保存！")
            self.accept()
        except Exception as e:
            error_msg = str(e)
            if "登录失败" in error_msg:
                QMessageBox.critical(self, "错误", "用户名或密码错误，请检查。")
            else:
                QMessageBox.critical(self, "错误", f"登录失败：{error_msg}")