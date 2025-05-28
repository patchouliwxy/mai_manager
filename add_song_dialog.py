from PyQt5.QtWidgets import QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit, QPushButton, QComboBox, QMessageBox

class AddSongDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("添加歌曲")
        self.resize(400, 300)

        layout = QVBoxLayout()

        # 歌曲标题
        layout.addWidget(QLabel("歌曲标题："))
        self.title_input = QLineEdit()
        layout.addWidget(self.title_input)

        # 艺术家
        layout.addWidget(QLabel("艺术家："))
        self.artist_input = QLineEdit()
        layout.addWidget(self.artist_input)

        # 类别
        layout.addWidget(QLabel("类别："))
        self.category_input = QLineEdit()
        layout.addWidget(self.category_input)

        # 版本
        layout.addWidget(QLabel("版本："))
        self.version_input = QLineEdit()
        layout.addWidget(self.version_input)

        # 谱面类型
        layout.addWidget(QLabel("谱面类型："))
        self.chart_type_combo = QComboBox()
        self.chart_type_combo.addItems(["std", "dx"])
        layout.addWidget(self.chart_type_combo)

        # 难度等级
        layout.addWidget(QLabel("难度（Basic, Advanced, Expert, Master, Re:Mas）："))
        self.basic_input = QLineEdit()
        self.advanced_input = QLineEdit()
        self.expert_input = QLineEdit()
        self.master_input = QLineEdit()
        self.remas_input = QLineEdit()
        difficulty_layout = QVBoxLayout()
        difficulty_layout.addWidget(QLabel("Basic:"))
        difficulty_layout.addWidget(self.basic_input)
        difficulty_layout.addWidget(QLabel("Advanced:"))
        difficulty_layout.addWidget(self.advanced_input)
        difficulty_layout.addWidget(QLabel("Expert:"))
        difficulty_layout.addWidget(self.expert_input)
        difficulty_layout.addWidget(QLabel("Master:"))
        difficulty_layout.addWidget(self.master_input)
        difficulty_layout.addWidget(QLabel("Re:Mas:"))
        difficulty_layout.addWidget(self.remas_input)
        layout.addLayout(difficulty_layout)

        # 确认和取消按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("添加")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_song_data(self):
        """获取输入的歌曲数据"""
        chart_type = self.chart_type_combo.currentText()
        song_data = {
            "title": self.title_input.text().strip(),
            "artist": self.artist_input.text().strip(),
            "category": self.category_input.text().strip(),
            "version": self.version_input.text().strip(),
            "chart_type": chart_type
        }
        # 根据谱面类型设置难度字段
        if chart_type == "std":
            song_data["lev_bas"] = self.basic_input.text().strip()
            song_data["lev_adv"] = self.advanced_input.text().strip()
            song_data["lev_exp"] = self.expert_input.text().strip()
            song_data["lev_mas"] = self.master_input.text().strip()
            song_data["lev_remas"] = self.remas_input.text().strip()
        else:  # dx
            song_data["dx_lev_bas"] = self.basic_input.text().strip()
            song_data["dx_lev_adv"] = self.advanced_input.text().strip()
            song_data["dx_lev_exp"] = self.expert_input.text().strip()
            song_data["dx_lev_mas"] = self.master_input.text().strip()
            song_data["dx_lev_remas"] = self.remas_input.text().strip()
        return song_data