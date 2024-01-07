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


basedir = os.path.dirname(__file__)


class ReflectiveEchoUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("ReflectiveEcho")
        self.setMinimumSize(400, 600)
        self.initUI()

    def initUI(self):
        self.main_widget = QWidget()
        self.main_layout = QVBoxLayout()

        self.default_layout = QVBoxLayout()

        logo_lable = QLabel()
        pixmap = QPixmap(os.path.join(basedir, "assets", "logo.png"))
        logo_lable.setPixmap(pixmap)
        logo_lable.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_layout.addWidget(logo_lable)

        title_label = QLabel("ReflectiveEcho")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_layout.addWidget(title_label)

        intro_label = QLabel("Welcome to ReflectiveEcho!")
        intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.default_layout.addWidget(intro_label)

        self.type_layout = QHBoxLayout()

        type_label = QLabel("Review Type:")
        type_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.type_layout.addWidget(type_label)

        type_combo = QComboBox()
        # Combo box options: Daily, Weekly, Monthly, Yearly
        type_combo.addItems(["Daily", "Weekly", "Monthly", "Yearly"])
        type_combo.setCurrentIndex(0)
        self.type_layout.addWidget(type_combo)
        self.default_layout.addLayout(self.type_layout)

        start_button = QPushButton("Start")
        start_button.clicked.connect(self.on_start_button_clicked)
        self.default_layout.addWidget(start_button)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.default_layout)

        # Set the main widget and layout
        self.main_widget.setLayout(self.main_layout)
        self.setCentralWidget(self.main_widget)
        
    def on_start_button_clicked(self):
        # TODO: Check if the user has set settings
            # TODO: If not, show the settings window
        # TODO: Get the review type from the combo box
        # TODO: Reload the main window UI to ChatUI
        # TODO: Invoke LLM to start the review
        
        print("Start button clicked")
