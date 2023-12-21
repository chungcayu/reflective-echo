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

from settings import SettingsDialog


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
