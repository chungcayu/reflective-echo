import sys
import os
from PyQt6.QtWidgets import (
    QMainWindow,
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QLabel,
    QPushButton,
    QComboBox,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt

from chat_ui import ChatUI

basedir = os.path.dirname(__file__)


class ReflectiveEchoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReflectiveEcho")
        self.setMinimumSize(400, 600)
        # self.setStyleSheet("background-color: #FFFBF5;")
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()

        # 窗口主布局
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.setSpacing(30)

        # 说明区域布局
        self.intro_layout = QVBoxLayout()
        self.intro_layout.setContentsMargins(0, 0, 0, 0)
        self.intro_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.intro_layout.setSpacing(10)

        # 应用Logo
        self.logo_lable = QLabel()
        self.logo_pixmap = QPixmap(os.path.join(basedir, "assets", "logo.png"))
        self.scaled_logo_pixmap = self.logo_pixmap.scaled(
            100,
            100,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        self.logo_lable.setPixmap(self.scaled_logo_pixmap)
        self.logo_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.intro_layout.addWidget(self.logo_lable)

        # 应用名称
        self.title_label = QLabel("ReflectiveEcho")
        self.title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.title_label.setStyleSheet(
            """
            QLabel {
                font-size: 30px;
                font-weight: bold;
            }
        """
        )
        self.intro_layout.addWidget(self.title_label)

        # 应用介绍
        self.intro_label = QLabel(
            """
            Unlock the power of your experiences with Echo, and make self-reflection as easy and natural as chatting with a friend.<br> \
            Choose a review type and start your journey now!"""
        )
        self.intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.intro_label.setWordWrap(True)
        self.intro_layout.addWidget(self.intro_label)

        # 选择Review类型
        self.type_layout = QHBoxLayout()

        type_label = QLabel("Review Type:")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_layout.addWidget(type_label)

        type_combo = QComboBox()
        type_combo.addItems(["Daily", "Weekly", "Monthly", "Yearly"])
        type_combo.setCurrentIndex(0)
        self.type_layout.addWidget(type_combo)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.on_start_button_clicked)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.intro_layout)
        self.main_layout.addLayout(self.type_layout)
        self.main_layout.addWidget(start_button)

        # Set the main widget and layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)

    def on_start_button_clicked(self):
        # TODO: Check if the user has set settings
        # TODO: If not, show the settings window
        # TODO: Get the review type from the combo box
        # TODO: Reload the main window UI to ChatUI
        self.switch_to_chat()
        # TODO: Invoke LLM to start the review

        print("Start button clicked")

    def switch_to_chat(self):
        self.chat_ui = ChatUI()
        self.takeCentralWidget()
        self.setCentralWidget(self.chat_ui)
