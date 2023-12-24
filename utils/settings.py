import os
import json
import sys
from PyQt6.QtWidgets import (
    QDialog,
    QGridLayout,
    QLabel,
    QLineEdit,
    QPushButton,
    QFrame,
    QFileDialog,
    QMessageBox,
)
from PyQt6.QtCore import Qt, QSize

from .security import encrypt_api_key, decrypt_api_key


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()
        self.init_ui()

    def init_ui(self):
        self.setWindowTitle("Settings")
        self.setFixedSize(600, 300)  # 固定设置面板大小

        self.grid_layout = QGridLayout(self)  # 使用网格布局

        # 用户布局和组件
        self.user_label = QLabel("用户称呼:")
        self.user_text = QLineEdit("")
        self.grid_layout.addWidget(self.user_label, 0, 0)  # 第一行，第一列
        self.grid_layout.addWidget(self.user_text, 0, 1, 1, 2)  # 第一行，占据第二、三列
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # 标签靠右对齐

        # 添加分割线
        self.grid_layout.addWidget(self.create_horizontal_separator(), 1, 0, 1, 3)

        # 保存路径布局和组件
        self.save_location_label = QLabel("保存路径:")
        self.save_location_text = QLineEdit("")
        self.save_location_text.setReadOnly(True)
        self.choose_folder_button = QPushButton("选择文件夹")
        self.choose_folder_button.clicked.connect(self.choose_folder)

        self.grid_layout.addWidget(self.save_location_label, 2, 0)
        self.grid_layout.addWidget(self.save_location_text, 2, 1)
        self.grid_layout.addWidget(self.choose_folder_button, 2, 2)
        self.save_location_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        # 添加分割线
        self.grid_layout.addWidget(self.create_horizontal_separator(), 3, 0, 1, 3)

        # API密钥布局和组件
        self.api_keys = {}
        self.add_api_key_row("OpenAI API Key:", self.grid_layout, 4)
        self.add_api_key_row("Xunfei App ID:", self.grid_layout, 5)
        self.add_api_key_row("Xunfei API Key:", self.grid_layout, 6)
        # self.add_api_key_row("Huoshan App ID:", self.grid_layout, 7)
        # self.add_api_key_row("Huoshan Access Token:", self.grid_layout, 8)
        # self.add_api_key_row("Huoshan Cluster ID:", self.grid_layout, 9)
        self.add_api_key_row("MiniMax Group ID:", self.grid_layout, 7)
        self.add_api_key_row("MiniMax API Key:", self.grid_layout, 8)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setFixedSize(100, 30)  # 固定大小
        self.save_button.clicked.connect(self.validate_and_save_settings)
        self.grid_layout.addWidget(
            self.save_button, 10, 1, Qt.AlignmentFlag.AlignCenter
        )  # 居中

        self.show()

    def create_horizontal_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:  # 确保用户选择了一个文件夹
            self.save_location_text.setText(folder_path)

    def add_api_key_row(self, label, layout, row):
        api_label = QLabel(label)
        layout.addWidget(api_label, row, 0)
        api_text = QLineEdit("")
        layout.addWidget(api_text, row, 1, 1, 2)
        self.api_keys[label] = api_text

    def validate_and_save_settings(self):
        if not self.is_all_input_valid():
            # 如果信息未完整填写，显示警告消息
            QMessageBox.warning(self, "输入验证", "请填写所有必需的信息。")
            return  # 返回设置面板，等待用户继续操作
        # 如果所有输入有效，则调用 save_settings 函数
        self.save_settings()

    def is_all_input_valid(self):
        if not self.user_text.text():
            return False

        # 检查保存路径是否已设置
        if not self.save_location_text.text():
            return False

        # 检查其他所有文本框是否填写
        for api_text in self.api_keys.values():
            if not api_text.text():
                return False

        return True

    def save_settings(self):
        try:
            # Create a dictionary to hold the settings
            settings_data = {
                "user_name": self.user_text.text(),
                "save_path": self.save_location_text.text(),
                "api_keys": {},
            }

            # 加密并保存 API 密钥
            for label, api_text in self.api_keys.items():
                # 生成一个安全的文件名，确保文件名对应于 API 密钥的名称
                safe_label = label.replace(" ", "_").lower().replace(":", "")
                encrypted_file_name = f"{safe_label}.encrypted"

                # 指定加密 API 密钥文件的保存路径
                encrypted_file_path = os.path.join("./data", encrypted_file_name)

                # 加密 API 密钥并将其写入文件
                encrypt_api_key(api_text.text(), encrypted_file_path)

                # 在设置字典中记录加密文件的路径
                settings_data["api_keys"][safe_label] = encrypted_file_path

            # Define the file path for settings.json
            settings_directory = "./data/"

            # Ensure the directory exists
            os.makedirs(settings_directory, exist_ok=True)

            # Write the settings data to the JSON file
            settings_file_path = os.path.join(settings_directory, "settings.json")
            with open(settings_file_path, "w", encoding="utf-8") as file:
                json.dump(settings_data, file, ensure_ascii=False, indent=4)

            QMessageBox.information(self, "保存成功", "设置已成功保存。")
            # 关闭设置面板
            self.accept()  # 如果是 QDialog，这会发送 accept 信号并关闭对话框
        except Exception as e:
            QMessageBox.warning(self, "保存失败", f"保存设置时出现错误：{e}")
            # 如果发生错误，不关闭对话框，允许用户修正


def load_settings():
    settings_file_path = "./data/settings.json"
    try:
        with open(settings_file_path, "r", encoding="utf-8") as file:
            return json.load(file)
    except FileNotFoundError:
        print("Settings file not found.")
        return {}
    except json.JSONDecodeError:
        print("Error decoding JSON from settings file.")
        return {}


# 提取用户姓名
def get_user_name():
    settings = load_settings()
    return settings.get("user_name", "")


# 提取文件保存路径
def get_save_path():
    settings = load_settings()
    return settings.get("save_path", "")


# 提取 API 密钥
def get_api_key(api_name):
    settings = load_settings()
    api_keys = settings.get("api_keys", {})
    encrypted_file_path = api_keys.get(api_name, "")
    if not encrypted_file_path:
        return ""
    try:
        api_key = decrypt_api_key(encrypted_file_path)
        return api_key
    except Exception as e:
        print(f"Error decrypting API key for {api_name}: {e}")
        return ""
