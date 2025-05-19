from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QGroupBox, QRadioButton,
    QCheckBox, QLineEdit, QPushButton, QLabel
)

class FilterDialog(QDialog):
    def __init__(self, versions, categories, parent=None):
        super().__init__(parent)
        self.setWindowTitle("筛选设置")
        self.setMinimumWidth(300)

        self.selected_type = None
        self.selected_versions = []
        self.selected_categories = []
        self.level_input = ""

        layout = QVBoxLayout()

        # 谱面类型
        type_group = QGroupBox("谱面类型")
        type_layout = QVBoxLayout()
        self.std_radio = QRadioButton("std")
        self.dx_radio = QRadioButton("dx")
        self.none_radio = QRadioButton("全部")
        self.none_radio.setChecked(True)
        type_layout.addWidget(self.none_radio)
        type_layout.addWidget(self.std_radio)
        type_layout.addWidget(self.dx_radio)
        type_group.setLayout(type_layout)
        layout.addWidget(type_group)

        # 版本多选
        self.version_boxes = []
        version_group = QGroupBox("版本")
        version_layout = QVBoxLayout()
        for v in versions:
            cb = QCheckBox(v)
            self.version_boxes.append(cb)
            version_layout.addWidget(cb)
        version_group.setLayout(version_layout)
        layout.addWidget(version_group)

        # 类别多选
        self.category_boxes = []
        category_group = QGroupBox("类别")
        category_layout = QVBoxLayout()
        for c in categories:
            cb = QCheckBox(c)
            self.category_boxes.append(cb)
            category_layout.addWidget(cb)
        category_group.setLayout(category_layout)
        layout.addWidget(category_group)

        # 等级
        level_layout = QVBoxLayout()
        level_layout.addWidget(QLabel("等级（可输入如12+）"))
        self.level_edit = QLineEdit()
        level_layout.addWidget(self.level_edit)
        layout.addLayout(level_layout)

        # 确认按钮
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("应用")
        cancel_btn = QPushButton("取消")
        ok_btn.clicked.connect(self.accept)
        cancel_btn.clicked.connect(self.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        layout.addLayout(btn_layout)

        self.setLayout(layout)

    def get_filters(self):
        if self.std_radio.isChecked():
            chart_type = "std"
        elif self.dx_radio.isChecked():
            chart_type = "dx"
        else:
            chart_type = None

        versions = [cb.text() for cb in self.version_boxes if cb.isChecked()]
        if not versions:
            versions = None

        categories = [cb.text() for cb in self.category_boxes if cb.isChecked()]
        if not categories:
            categories = None

        level = self.level_edit.text().strip()
        if level == "":
            level = None

        return chart_type, versions, level, categories
