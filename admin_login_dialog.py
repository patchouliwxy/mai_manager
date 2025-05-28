from PyQt5.QtWidgets import QDialog, QLabel, QLineEdit, QPushButton, QVBoxLayout, QMessageBox

class AdminLoginDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("管理员登录")
        self.resize(300, 200)
        self.parent = parent

        layout = QVBoxLayout()
        layout.addWidget(QLabel("请输入管理员用户名和密码："))
        layout.addWidget(QLabel("用户名："))
        self.username_input = QLineEdit()
        layout.addWidget(self.username_input)

        layout.addWidget(QLabel("密码："))
        self.password_input = QLineEdit()
        self.password_input.setEchoMode(QLineEdit.Password)
        layout.addWidget(self.password_input)

        self.login_btn = QPushButton("登录")
        self.login_btn.clicked.connect(self.verify_admin)
        layout.addWidget(self.login_btn)

        self.setLayout(layout)

    def verify_admin(self):
        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "警告", "请输入用户名和密码。")
            return

        if username == "guanliyuan" and password == "1919810":
            QMessageBox.information(self, "成功", "管理员登录成功！")
            self.accept()
        else:
            QMessageBox.critical(self, "错误", "用户名或密码错误，请检查。")