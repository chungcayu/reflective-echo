from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QFileDialog,
)
from PyQt6.QtCore import Qt, QSize


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.setFixedSize(600, 300)  # 固定设置面板大小

        self.grid_layout = QGridLayout(self)  # 使用网格布局

        # 用户布局和组件
        self.user_label = QLabel("用户称呼:")
        # user_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # 标签靠右对齐
        self.grid_layout.addWidget(self.user_label, 0, 0)  # 第一行，第一列
        self.user_text = QLineEdit("")
        self.grid_layout.addWidget(self.user_text, 0, 1, 1, 2)  # 第一行，占据第二、三列
        # 添加分割线
        self.grid_layout.addWidget(self.create_horizontal_separator(), 1, 0, 1, 3)

        # 保存路径布局和组件
        self.save_location_label = QLabel("保存路径:")
        # save_location_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.grid_layout.addWidget(self.save_location_label, 2, 0)
        self.save_location_text = QLineEdit("")
        self.grid_layout.addWidget(self.save_location_text, 2, 1)
        self.choose_folder_button = QPushButton("选择文件夹")
        self.choose_folder_button.clicked.connect(self.choose_folder)
        self.grid_layout.addWidget(self.choose_folder_button, 2, 2)

        # 添加分割线
        self.grid_layout.addWidget(self.create_horizontal_separator(), 3, 0, 1, 3)

        # API密钥布局和组件
        self.add_api_key_row("OpenAI API Key:", self.grid_layout, 4)
        self.add_api_key_row("讯飞 App ID:", self.grid_layout, 5)
        self.add_api_key_row("讯飞 API Key:", self.grid_layout, 6)
        self.add_api_key_row("火山引擎 App ID:", self.grid_layout, 7)
        self.add_api_key_row("火山引擎 Access Token:", self.grid_layout, 8)
        self.add_api_key_row("火山引擎 Cluster ID:", self.grid_layout, 9)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setFixedSize(100, 30)  # 固定大小
        self.save_button.clicked.connect(self.save_settings)
        self.grid_layout.addWidget(
            self.save_button, 10, 1, Qt.AlignmentFlag.AlignCenter
        )  # 居中

    def add_api_key_row(self, label_text, layout, row):
        api_key_label = QLabel(label_text)
        # api_key_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(api_key_label, row, 0)
        api_text = QLineEdit("")
        # api_text.setFixedSize(self.input_width, self.input_height)
        layout.addWidget(api_text, row, 1, 1, 2)  # 占据第二、三列

    def create_horizontal_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder:  # 确保用户选择了一个文件夹
            self.save_location_text.setText(folder)

    def save_settings(self):
        api_keys = [edit.text() for edit in self.api_key_inputs]
        print("API Keys:", api_keys)  # 例如，打印API键以演示
        print("Settings saved!")
        self.accept()
