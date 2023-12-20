import sys
from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QApplication,
    QMainWindow,
    QPushButton,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QWidget,
    QTextEdit,
    QMessageBox,
)


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

        button_style = (
            "QPushButton {"
            "   width: 80px;"  # 设置宽度
            "   height: 30px;"  # 设置高度
            "   border: 1px solid black;"
            "   border-radius: 5px;"  # 设置圆角
            "   background-color: lightgray;"  # 可选的背景颜色
            "}"
        )

        # Side Layout
        self.side_layout = QVBoxLayout()
        self.side_layout.setSpacing(
            10
        )  # This sets the space between widgets in the layout.
        self.side_layout.setAlignment(
            Qt.AlignmentFlag.AlignTop | Qt.AlignmentFlag.AlignLeft
        )

        # Create and style the buttons
        self.button_setting = QPushButton("设置")
        self.button_setting.clicked.connect(self.openSettingsDialog)
        self.button_view = QPushButton("查看")
        self.button_view.clicked.connect(self.showSavePath)
        self.button_about = QPushButton("关于")
        self.button_about.clicked.connect(self.showAboutInfo)
        self.button_help = QPushButton("帮助")
        self.button_help.clicked.connect(self.showHelpInfo)

        # Set a fixed width for the side buttons and margins to zero for them to be at the very edge.
        # self.button_width = 100
        # self.button_setting.setFixedWidth(self.button_width)
        # self.button_view.setFixedWidth(self.button_width)
        # self.button_about.setFixedWidth(self.button_width)
        # self.button_help.setFixedWidth(self.button_width)

        # Add buttons to the layout with a margin at the top
        self.side_layout.addWidget(self.button_setting)
        self.side_layout.addWidget(self.button_view)
        self.side_layout.addWidget(self.button_about)
        self.side_layout.addWidget(self.button_help)

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
            "   border: 1px solid black;"
            "   border-radius: 10px;"  # Set the corner radius here
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
            "   border: 1px solid black;"  # Adjusted border width
            "   border-radius: 10px;"  # Radius for rounded corners
            "   padding: 5px;"  # Add padding
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

        # self.button_start.setFixedSize(100, 30)
        # self.bottom_speak.setFixedSize(100, 30)
        # self.bottom_submit.setFixedSize(100, 30)
        # self.bottom_finish.setFixedSize(100, 30)

        self.button_layout.addWidget(self.button_start)
        self.button_layout.addWidget(self.bottom_speak)
        self.button_layout.addWidget(self.bottom_submit)
        self.button_layout.addWidget(self.bottom_finish)

        self.display_layout.addLayout(self.assistant_layout)
        self.display_layout.addLayout(self.user_layout)
        self.display_layout.addLayout(self.button_layout)

        self.setStyleSheet(button_style)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.side_layout)
        self.main_layout.addLayout(self.display_layout)

        # Set the main widget and layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def openSettingsDialog(self):
        pass

    def showSavePath(self):
        pass

    def showAboutInfo(self):
        QMessageBox.information(self, "关于", "这是关于应用的介绍。")

    def showHelpInfo(self):
        QMessageBox.information(self, "帮助", "这是使用说明。")


if __name__ == "__main__":
    app = QApplication(sys.argv)
    ex = ReflectiveEchoUI()
    ex.show()
    sys.exit(app.exec())
