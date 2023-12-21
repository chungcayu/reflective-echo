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
        self.setFixedSize(400, 300)  # 固定设置面板大小

        grid_layout = QGridLayout(self)  # 使用网格布局

        # 用户布局和组件
        grid_layout.addWidget(QLabel("User:"), 0, 0)  # 第一行，第一列
        user_text = QLineEdit("")
        user_text.setFixedSize(100, 20)  # 固定大小
        grid_layout.addWidget(user_text, 0, 1, 1, 2)  # 第一行，占据第二、三列

        # 添加分割线
        grid_layout.addWidget(self.create_horizontal_separator(), 1, 0, 1, 3)

        # 保存路径布局和组件
        grid_layout.addWidget(QLabel("Document Save Location:"), 2, 0)
        save_location_text = QLineEdit("")
        grid_layout.addWidget(save_location_text, 2, 1)
        choose_folder_button = QPushButton("Choose Folder")
        choose_folder_button.clicked.connect(self.choose_folder)
        grid_layout.addWidget(choose_folder_button, 2, 2)

        # 添加分割线
        grid_layout.addWidget(self.create_horizontal_separator(), 3, 0, 1, 3)

        # API密钥布局和组件
        self.add_api_key_row("OpenAI API Key:", grid_layout, 4)
        self.add_api_key_row("Xunfei API Key:", grid_layout, 5)
        self.add_api_key_row("Huoshan API Key:", grid_layout, 6)

        # 保存按钮
        save_button = QPushButton("Save")
        save_button.setFixedSize(100, 30)  # 固定大小
        save_button.clicked.connect(self.save_settings)
        grid_layout.addWidget(save_button, 7, 1, Qt.AlignmentFlag.AlignCenter)  # 居中

    def add_api_key_row(self, label_text, layout, row):
        layout.addWidget(QLabel(label_text), row, 0)
        api_text = QLineEdit("")
        api_text.setFixedSize(100, 20)  # 固定大小
        layout.addWidget(api_text, row, 1, 1, 2)  # 占据第二、三列

    def create_horizontal_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:  # 确保用户选择了一个文件夹
            self.save_location_text.setText(folder)

    def save_settings(self):
        api_keys = [edit.text() for edit in self.api_key_inputs]
        print("API Keys:", api_keys)  # 例如，打印API键以演示
        print("Settings saved!")
        self.accept()
