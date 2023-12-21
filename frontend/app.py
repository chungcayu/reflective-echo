import sys
from PyQt6.QtCore import Qt, QUrl
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QPushButton,
    QLabel,
    QTextEdit,
    QLineEdit,
    QMessageBox,
    QFileDialog,
)
from PyQt6.QtGui import QDesktopServices, QAction


class SettingsDialog(QDialog):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Settings")
        self.settings_layout = QVBoxLayout(self)  # 主布局

        # 子布局
        self.info_layout = QVBoxLayout()
        self.apikey_layout = QVBoxLayout()  # 子布局不直接关联到self

        # 用户布局和组件
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("User: ")
        self.user_text = QLineEdit("")
        self.user_layout.addWidget(self.user_label)
        self.user_layout.addWidget(self.user_text)

        # 保存路径布局和组件
        self.save_location_layout = QHBoxLayout()
        self.save_location_label = QLabel("Document Save Location: ")
        self.save_location_text = QLineEdit("")
        self.choose_folder_button = QPushButton("Choose Folder")
        self.choose_folder_button.clicked.connect(self.choose_folder)

        self.save_location_layout.addWidget(self.save_location_label)
        self.save_location_layout.addWidget(self.save_location_text)
        self.save_location_layout.addWidget(self.choose_folder_button)

        # OpenAI布局和组件
        self.openai_layout = QHBoxLayout()
        self.openai_label = QLabel("OpenAI API Key: ")
        self.openai_text = QLineEdit("")
        self.openai_layout.addWidget(self.openai_label)
        self.openai_layout.addWidget(self.openai_text)

        # 讯飞布局和组件
        self.xunfei_layout = QHBoxLayout()
        self.xunfei_label = QLabel("Xunfei API Key: ")
        self.xunfei_text = QLineEdit("")
        self.xunfei_layout.addWidget(self.xunfei_label)
        self.xunfei_layout.addWidget(self.xunfei_text)

        # 火山布局和组件
        self.huoshan_layout = QHBoxLayout()
        self.huoshan_label = QLabel("Huoshan API Key: ")
        self.huoshan_text = QLineEdit("")
        self.huoshan_layout.addWidget(self.huoshan_label)
        self.huoshan_layout.addWidget(self.huoshan_text)

        # 将子布局添加到API键布局
        self.apikey_layout.addLayout(self.openai_layout)
        self.apikey_layout.addLayout(self.xunfei_layout)
        self.apikey_layout.addLayout(self.huoshan_layout)

        # 保存按钮
        self.save_button = QPushButton("Save")
        self.save_button.clicked.connect(self.save_settings)

        # 将API键布局和保存按钮添加到主布局
        self.settings_layout.addLayout(self.user_layout)
        self.settings_layout.addLayout(self.save_location_layout)
        self.settings_layout.addLayout(self.apikey_layout)
        self.settings_layout.addWidget(self.save_button)

        # 存储所有API文本框引用，以便于在save_settings中使用
        self.api_key_inputs = [self.openai_text, self.xunfei_text, self.huoshan_text]

    def choose_folder(self):
        folder = QFileDialog.getExistingDirectory(self, "Select Folder")
        if folder:  # 确保用户选择了一个文件夹
            self.save_location_text.setText(folder)

    def save_settings(self):
        api_keys = [edit.text() for edit in self.api_key_inputs]
        print("API Keys:", api_keys)  # 例如，打印API键以演示
        print("Settings saved!")
        self.accept()


class ReflectiveEchoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reflective Echo")
        self.setGeometry(100, 100, 800, 600)
        self.setFixedSize(800, 600)
        self.initUI()

    def initUI(self):
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

        button_style = (
            "QPushButton {"
            "   width: 80px;"  # 设置宽度
            "   height: 30px;"  # 设置高度
            "   border: 1px solid gray;"
            "   border-radius: 5px;"  # 设置圆角
            "   background-color: gray;"  # 可选的背景颜色
            "}"
        )

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
        self.assistant_label = QLabel("Assistant: ")
        self.assistant_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )

        self.assistant_message = QLabel(
            "ReflectiveEcho, the AI-driven conversation partner that makes weekly reflection as easy and natural as chatting with a friend."
        )
        self.assistant_message.setWordWrap(True)
        self.assistant_message.setFixedSize(550, 200)
        self.assistant_message.setStyleSheet(
            "QLabel {"
            "   border: 1px solid gray;"
            "   border-radius: 5px;"  # Set the corner radius here
            "   padding: 5px;"
            "}"
        )
        # assistant_message.setAlignment(
        #     Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignTop
        # )
        self.assistant_layout.addWidget(self.assistant_label)
        self.assistant_layout.addWidget(self.assistant_message)

        # User layout
        self.user_layout = QHBoxLayout()
        self.user_label = QLabel("User: ")
        self.user_label.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignRight
        )
        self.user_message = QTextEdit("")
        self.user_message.setFixedSize(550, 320)
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

        self.button_start = QPushButton("开始复盘")
        self.bottom_speak = QPushButton("🎙️")
        self.bottom_submit = QPushButton("⌨️")
        self.bottom_finish = QPushButton("结束复盘")

        self.button_layout.addWidget(self.button_start)
        self.button_layout.addWidget(self.bottom_speak)
        self.button_layout.addWidget(self.bottom_submit)
        self.button_layout.addWidget(self.bottom_finish)

        self.display_layout.addLayout(self.assistant_layout)
        self.display_layout.addLayout(self.user_layout)
        self.display_layout.addLayout(self.button_layout)

        self.setStyleSheet(button_style)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.display_layout)

        # Set the main widget and layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def openSettingsDialog(self):
        dialog = SettingsDialog()
        if dialog.exec() == QDialog.DialogCode.Accepted:
            # 这里可以处理设置面板关闭后的逻辑
            pass

    def showSavePath(self):
        pass

    def showAboutInfo(self):
        QDesktopServices.openUrl(QUrl("https://github.com/chungcayu/reflective-echo"))

    def showHelpInfo(self):
        QDesktopServices.openUrl(QUrl("https://github.com/chungcayu/reflective-echo"))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ReflectiveEcho")
    ex = ReflectiveEchoUI()
    ex.show()
    sys.exit(app.exec())
