import os
import platform

import subprocess
from PyQt6.QtWidgets import (
    QMainWindow,
    QWidget,
    QGridLayout,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QTextEdit,
    QLineEdit,
    QPushButton,
    QFrame,
    QFileDialog,
    QDialog,
    QMessageBox,
    QLabel,
    QScrollArea,
)
from PyQt6.QtCore import pyqtSignal, Qt, QUrl, QTimer, QThread
from PyQt6.QtGui import QDesktopServices, QAction, QTextCursor, QPixmap, QCursor

from settings_manager import SettingsManager
from gpt_api_thread import GptApiThread
from tts_thread import TtsThread
from stt_thread import SttThread

import logging

logger = logging.getLogger(__name__)


class SettingsDialog(QDialog):
    def __init__(self, settings_manager):
        super(SettingsDialog, self).__init__()
        self.settings_manager = settings_manager
        self.settings_dialog = None
        self.setWindowTitle("设置")
        self.setGeometry(100, 100, 600, 300)  # Adjusted for potential extra size
        self.setFixedSize(600, 300)
        self.initUI()
        self.load_settings()

    def initUI(self):
        self.grid_layout = QGridLayout(self)

        # 用户布局和组件
        self.user_label = QLabel("用户称呼:")
        self.user_label.setAlignment(Qt.AlignmentFlag.AlignRight)  # 标签靠右对齐

        self.user_text = QLineEdit("")

        self.grid_layout.addWidget(self.user_label, 0, 0)  # 第一行，第一列
        self.grid_layout.addWidget(self.user_text, 0, 1, 1, 2)  # 第一行，占据第二、三列
        self.grid_layout.addWidget(self.create_horizontal_separator(), 1, 0, 1, 3)

        # 保存路径布局和组件
        self.save_location_label = QLabel("保存路径:")
        self.save_location_label.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.save_location_text = QLineEdit("")
        self.save_location_text.setReadOnly(True)

        self.choose_folder_button = QPushButton("选择文件夹")
        self.choose_folder_button.clicked.connect(self.choose_folder)

        self.grid_layout.addWidget(self.save_location_label, 2, 0)
        self.grid_layout.addWidget(self.save_location_text, 2, 1)
        self.grid_layout.addWidget(self.choose_folder_button, 2, 2)
        self.grid_layout.addWidget(self.create_horizontal_separator(), 3, 0, 1, 3)

        # API密钥布局和组件
        self.openai_apikey_label = QLabel("OpenAI API Key:")
        self.openai_apikey_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.openai_apikey_text = QLineEdit("")
        self.openai_apikey_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.grid_layout.addWidget(self.openai_apikey_label, 4, 0)
        self.grid_layout.addWidget(self.openai_apikey_text, 4, 1, 1, 2)

        self.xunfei_appid_label = QLabel("Xunfei App ID:")
        self.xunfei_appid_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.xunfei_appid_text = QLineEdit("")
        self.xunfei_appid_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.grid_layout.addWidget(self.xunfei_appid_label, 5, 0)
        self.grid_layout.addWidget(self.xunfei_appid_text, 5, 1, 1, 2)

        self.xunfei_apikey_label = QLabel("Xunfei API Key:")
        self.xunfei_apikey_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.xunfei_apikey_text = QLineEdit("")
        self.xunfei_apikey_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.grid_layout.addWidget(self.xunfei_apikey_label, 6, 0)
        self.grid_layout.addWidget(self.xunfei_apikey_text, 6, 1, 1, 2)

        # self.minimax_groupid_label = QLabel("MiniMax Group ID:")
        # self.minimax_groupid_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.minimax_groupid_text = QLineEdit("")
        # self.minimax_groupid_text.setEchoMode(QLineEdit.EchoMode.Password)
        # self.grid_layout.addWidget(self.minimax_groupid_label, 7, 0)
        # self.grid_layout.addWidget(self.minimax_groupid_text, 7, 1, 1, 2)

        # self.minimax_apikey_label = QLabel("MiniMax API Key:")
        # self.minimax_apikey_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.minimax_apikey_text = QLineEdit("")
        # self.minimax_apikey_text.setEchoMode(QLineEdit.EchoMode.Password)
        # self.grid_layout.addWidget(self.minimax_apikey_label, 8, 0)
        # self.grid_layout.addWidget(self.minimax_apikey_text, 8, 1, 1, 2)

        self.volcano_appid_label = QLabel("Volcano App ID:")
        self.volcano_appid_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.volcano_appid_text = QLineEdit("")
        self.volcano_appid_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.grid_layout.addWidget(self.volcano_appid_label, 7, 0)
        self.grid_layout.addWidget(self.volcano_appid_text, 7, 1, 1, 2)

        self.volcano_access_token_label = QLabel("Volcano Access Token:")
        self.volcano_access_token_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        self.volcano_access_token_text = QLineEdit("")
        self.volcano_access_token_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.grid_layout.addWidget(self.volcano_access_token_label, 8, 0)
        self.grid_layout.addWidget(self.volcano_access_token_text, 8, 1, 1, 2)

        # 保存按钮
        self.save_button = QPushButton("保存")
        self.save_button.setFixedSize(100, 30)  # 固定大小
        self.save_button.clicked.connect(self.validate_and_save_settings)
        self.grid_layout.addWidget(
            self.save_button, 10, 1, Qt.AlignmentFlag.AlignCenter
        )  # 居中

        self.show()

        # Connect the confirm button to the save method
        self.save_button.clicked.connect(self.save_settings)

    def load_settings(self):
        # Load current settings into the dialog fields
        self.user_text.setText(self.settings_manager.get_setting("user_name") or "")
        self.save_location_text.setText(
            self.settings_manager.get_setting("save_location") or ""
        )
        self.openai_apikey_text.setText(
            self.settings_manager.get_setting("openai_api_key") or ""
        )
        self.xunfei_appid_text.setText(
            self.settings_manager.get_setting("xunfei_app_id") or ""
        )
        self.xunfei_apikey_text.setText(
            self.settings_manager.get_setting("xunfei_api_key") or ""
        )
        # self.minimax_groupid_text.setText(
        #     self.settings_manager.get_setting("minimax_group_id") or ""
        # )
        # self.minimax_apikey_text.setText(
        #     self.settings_manager.get_setting("minimax_api_key") or ""
        # )
        self.volcano_appid_text.setText(
            self.settings_manager.get_setting("volcano_app_id") or ""
        )
        self.volcano_access_token_text.setText(
            self.settings_manager.get_setting("volcano_access_token") or ""
        )

    def open_settings_dialog(self):
        if self.settings_dialog is None:
            self.settings_dialog = SettingsDialog(self.settings_manager)
        self.settings_dialog.show()  # 显示设置对话框

    def showEvent(self, event):
        """重写 showEvent，在每次窗口显示时重新加载设置"""
        print("显示设置对话框，正在重新加载设置...")
        self.load_settings()
        super(SettingsDialog, self).showEvent(event)

    def create_horizontal_separator(self):
        separator = QFrame()
        separator.setFrameShape(QFrame.Shape.HLine)
        separator.setFrameShadow(QFrame.Shadow.Sunken)
        return separator

    def choose_folder(self):
        folder_path = QFileDialog.getExistingDirectory(self, "选择文件夹")
        if folder_path:  # 确保用户选择了一个文件夹
            self.save_location_text.setText(folder_path)

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
        if not self.openai_apikey_text.text():
            return False
        if not self.xunfei_appid_text.text():
            return False
        if not self.xunfei_apikey_text.text():
            return False
        # if not self.minimax_groupid_text.text():
        #     return False
        # if not self.minimax_apikey_text.text():
        #     return False
        if not self.volcano_appid_text.text():
            return False
        if not self.volcano_access_token_text.text():
            return False
        return True

    def save_settings(self):
        # Collect the settings and use the settings_manager to save
        new_settings = {
            "user_name": self.user_text.text(),
            "save_location": self.save_location_text.text(),
            "openai_api_key": self.openai_apikey_text.text(),
            "xunfei_app_id": self.xunfei_appid_text.text(),
            "xunfei_api_key": self.xunfei_apikey_text.text(),
            # "minimax_group_id": self.minimax_groupid_text.text(),
            # "minimax_api_key": self.minimax_apikey_text.text(),
            "volcano_app_id": self.volcano_appid_text.text(),
            "volcano_access_token": self.volcano_access_token_text.text(),
        }
        self.settings_manager.save_settings(new_settings)
        self.accept()


class ReflectiveEchoUI(QMainWindow):
    # Signals
    update_assistant_signal = pyqtSignal(str)
    start_tts_signal = pyqtSignal(str)  # Trigger TTS
    start_stt_signal = pyqtSignal()  # Trigger STT
    finish_session_signal = pyqtSignal()  # Finish the reflection session

    def __init__(self, settings_manager):
        super().__init__()
        self.setWindowTitle("Reflective Echo")
        self.setGeometry(100, 100, 700, 600)
        self.setMinimumSize(700, 600)
        # self.setFixedSize(700, 600)

        # self.settings_manager = SettingsManager()
        self.settings_manager = settings_manager
        self.gpt_api_thread = None
        self.stt_thread = None
        self.update_assistant_signal.connect(self.actual_update_assistant_message)

        self.tts_thread = TtsThread(QThread)
        self.tts_thread.errorOccurred.connect(self.handle_tts_error)

        self.initUI()

    def initUI(self):
        # We will only change the signal connections for the buttons
        # Create the main widget and layout
        self.main_widget = QWidget()
        # main_layout = QVBoxLayout()
        self.main_layout = QHBoxLayout()

        # 创建菜单栏和菜单
        menubar = self.menuBar()
        settingsMenu = menubar.addMenu("设置")
        viewMenu = menubar.addMenu("查看")
        aboutMenu = menubar.addMenu("关于")
        helpMenu = menubar.addMenu("帮助")

        # 创建动作并添加到菜单
        settingAction = QAction("设置", self)
        settingAction.triggered.connect(self.openSettingsDialog)
        settingsMenu.addAction(settingAction)

        viewAction = QAction("查看", self)
        viewAction.triggered.connect(self.showSavePath)
        viewMenu.addAction(viewAction)

        aboutAction = QAction("关于", self)
        aboutAction.triggered.connect(self.showAboutInfo)
        aboutMenu.addAction(aboutAction)

        helpAction = QAction("帮助", self)
        helpAction.triggered.connect(self.showHelpInfo)
        helpMenu.addAction(helpAction)

        # Main layout
        self.display_layout = QVBoxLayout()
        self.display_layout.setSpacing(
            10
        )  # This sets the space between widgets in the layout.
        self.display_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        # Assistant layout
        self.assistant_layout = QHBoxLayout()
        self.assistant_layout.setContentsMargins(0, 0, 0, 0)
        self.assistant_label = QLabel("Echo: ")
        self.assistant_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        self.assistant_message = QLabel(
            """
            ReflectiveEcho, the AI-driven conversation partner that makes weekly reflection as easy and natural as chatting with a friend.
            """
        )
        self.assistant_message.setWordWrap(True)
        # self.assistant_message.setFixedSize(600, 200)
        self.assistant_message.setStyleSheet(
            "QLabel {"
            # "   border: 1px solid gray;"
            # "   border-radius: 5px;"  # Set the corner radius here
            "   margin: 0px 0 0px 0;"
            "   padding-top: 0px;"
            "   padding-bottom: 0px;"
            "   padding-left: 5px;"
            "   padding-right: 5px;"
            "}"
        )
        # 创建一个 QScrollArea 并将 QLabel 添加到其中
        scroll_area = QScrollArea()
        scroll_area.setContentsMargins(0, 0, 0, 0)
        scroll_area.setWidgetResizable(True)  # 设置为可调整大小
        scroll_area.setWidget(self.assistant_message)

        scroll_area.setStyleSheet(
            """
            QScrollArea {
                border: 1px solid gray;
                border-radius: 5px;
            }
            QScrollBar:vertical {
                border: none;
                width: 5px;  /* 更细的滚动条 */
                margin: 0px 0 0px 0;
                border-radius: 2px;
            }
            QScrollBar::handle:vertical {
                background: darkgray;  /* 滚动条手柄的颜色 */
                min-height: 10px;
                border-radius: 2px;
            }
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {
                border: none;
                background: none;
            }
            QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {
                background: none;
            }
            QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {
                background: none;
            }
        """
        )

        scroll_area.setFixedSize(600, 200)

        self.assistant_layout.addWidget(self.assistant_label)
        # self.assistant_layout.addWidget(self.assistant_message)
        self.assistant_layout.addWidget(scroll_area)

        # User layout
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("User: ")
        self.user_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.user_message = QTextEdit("")
        self.user_message.setFixedSize(600, 320)
        self.user_message.setStyleSheet(
            "QTextEdit {"
            "   border: 1px solid gray;"  # Adjusted border width
            "   border-radius: 5px;"  # Radius for rounded corners
            "   padding: 5px;"  # Add padding
            "   background-color: lightgray;"
            "}"
            "QScrollBar:vertical {"
            "   background: transparent;"  # Makes the scrollbar background transparent
            "}"
        )
        # user_message.setAlignment(Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignTop)
        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_message)

        # Button layout
        self.button_layout = QHBoxLayout()
        self.button_layout.setAlignment(
            Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignRight
        )

        button_style = (
            "QPushButton {"
            "   width: 80px;"  # 设置宽度
            "   height: 30px;"  # 设置高度
            "   border: 1px solid gray;"
            "   border-radius: 5px;"  # 设置圆角
            "   background-color: gray;"  # 可选的背景颜色
            "}"
            "QPushButton:hover {"
            "   background-color: silver;"  # 悬停时的背景颜色
            "}"
            "QPushButton:pressed {"
            "   background-color: #A9A9A9;"  # 按下时的背景颜色
            "}"
        )

        self.button_start = QPushButton("开始复盘")
        self.button_start.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_start.clicked.connect(self.on_start_reflection_clicked)

        self.button_speak = QPushButton("🎙️")
        self.button_speak.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_speak.clicked.connect(self.on_mic_button_clicked)

        self.button_submit = QPushButton("⌨️")
        self.button_submit.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_submit.clicked.connect(self.on_keyboard_button_clicked)

        self.button_finish = QPushButton("结束复盘")
        self.button_finish.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.button_finish.clicked.connect(self.on_finish_reflection_clicked)

        self.button_layout.addWidget(self.button_start)
        self.button_layout.addWidget(self.button_speak)
        self.button_layout.addWidget(self.button_submit)
        self.button_layout.addWidget(self.button_finish)

        self.display_layout.addLayout(self.assistant_layout)
        self.display_layout.addLayout(self.user_layout)
        self.display_layout.addLayout(self.button_layout)

        self.setStyleSheet(button_style)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.display_layout)

        # Set the main widget and layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def on_start_reflection_clicked(self):
        """
        当“开始复盘”按钮被点击时调用此方法。
        """
        if not self.settings_manager.isSettingsFilled():
            # 如果没有设置，则打开设置对话框
            self.promptForSetting()
            return
        else:
            # 更新助手窗口的消息
            self.update_assistant_message("准备复盘...")
            user_name = self.settings_manager.get_setting("user_name")

        # 创建并启动 GPT API 通信线程
        if not self.gpt_api_thread:
            self.gpt_api_thread = GptApiThread(user_name)
            self.gpt_api_thread.response_signal.connect(self.handle_gpt_response)
            self.gpt_api_thread.update_message_signal.connect(
                self.update_assistant_message
            )
            self.gpt_api_thread.start()

    def promptForSetting(self):
        msgBox = QMessageBox()
        customIcon = QPixmap("../assets/logo.png")
        msgBox.setIconPixmap(
            customIcon.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        )
        msgBox.setText("未填写设置信息，是否打开设置？")
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        reply = msgBox.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.openSettingsDialog()

    def handle_gpt_response(self, response):
        # 处理从GPT API获得的响应
        self.current_gpt_response = response
        self.tts_thread = TtsThread(response)
        self.tts_thread.finished_signal.connect(self.on_tts_finished)
        self.tts_thread.start()

        # self.update_assistant_message(response)

    def on_tts_finished(self):
        self.update_assistant_message(self.current_gpt_response)

    def on_keyboard_button_clicked(self):
        """
        当“键盘”按钮被点击时调用此方法。
        """
        # 从文本框获取用户输入
        user_message = self.user_message.toPlainText()
        # 检查文本框是否为空
        if not user_message.strip():  # 使用 .strip() 移除可能的空白字符
            QMessageBox.warning(self, "提示", "输入内容不能为空")
            return
        # 更新助手窗口的消息为“Echo正在思考...”
        # QTimer.singleShot(0, lambda: self.update_assistant_message("Echo正在思考..."))
        self.update_assistant_message("Echo正在思考...")

        # 清空文本框
        self.user_message.clear()
        # 启动 GPT API 通信线程
        if self.gpt_api_thread:
            self.gpt_api_thread.new_user_message_signal.emit(user_message)

    def on_mic_button_clicked(self):
        # # 获取讯飞 API 的配置
        # xf_app_id = self.settings_manager.get_setting("xf_app_id")
        # xf_api_key = self.settings_manager.get_setting("xf_api_key")

        # 创建并启动 STT 线程
        if not self.stt_thread or not self.stt_thread.isRunning():
            self.stt_thread = SttThread()
            self.stt_thread.text_updated_signal.connect(self.update_user_message)
            self.stt_thread.start()

    def on_finish_reflection_clicked(self):
        if self.gpt_api_thread:
            chatlog_path = self.gpt_api_thread.save_chatlog()
            self.gpt_api_thread.generate_report(chatlog_path)

    def actual_update_assistant_message(self, message):
        # 实际更新UI的方法
        self.assistant_message.setText(message)

    # Update functions will remain to update the UI in response to signals
    def update_assistant_message(self, message):
        # 发射信号以更新助手消息
        self.update_assistant_signal.emit(message)

    # def update_user_message(self, message):
    #     # Update the user message in the UI
    #     self.user_message.setText(message)

    def update_user_message(self, new_text):
        # 将新识别的文本添加到文本框现有内容的末尾
        current_text = self.user_message.toPlainText()
        updated_text = current_text + new_text
        self.user_message.setText(updated_text)

        self.user_message.moveCursor(QTextCursor.MoveOperation.End)

    # ... (Other UI related methods like openSettingsDialog, showSavePath, etc.)
    def openSettingsDialog(self):
        settings_dialog = SettingsDialog(self.settings_manager)
        settings_dialog.exec()

    def showSavePath(self):
        save_location = self.settings_manager.get_setting("save_location")
        if save_location:
            if platform.system() == "Windows":
                os.startfile(save_location)
            elif platform.system() == "Darwin":  # macOS
                subprocess.Popen(["open", save_location])
            else:  # Linux and other OS
                subprocess.Popen(["xdg-open", save_location])
        else:
            # 处理没有设置保存路径的情况
            self.promptForSettingSavePath()

    def promptForSettingSavePath(self):
        msgBox = QMessageBox()
        customIcon = QPixmap("../assets/reflective-echo-logo.png")
        msgBox.setIconPixmap(
            customIcon.scaled(50, 50, Qt.AspectRatioMode.KeepAspectRatio)
        )
        msgBox.setText("未设置保存路径，是否打开设置？")
        msgBox.setStandardButtons(
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        reply = msgBox.exec()

        if reply == QMessageBox.StandardButton.Yes:
            self.openSettingsDialog()

    def showAboutInfo(self):
        QDesktopServices.openUrl(QUrl("https://github.com/chungcayu/reflective-echo"))

    def showHelpInfo(self):
        QDesktopServices.openUrl(
            QUrl(
                "https://github.com/chungcayu/reflective-echo/blob/main/quick-start.md"
            )
        )

    def handle_tts_error(self, title, message):
        QMessageBox.critical(self, title, message)
