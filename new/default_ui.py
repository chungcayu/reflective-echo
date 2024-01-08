import sys
import os
from PyQt6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QLabel,
    QPushButton,
    QComboBox,
)
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt, QUrl


basedir = os.path.dirname(__file__)


class DefaultUI(QWidget):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.initUI()

    def initUI(self):
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
                color: #000000;
            }
        """
        )
        self.intro_layout.addWidget(self.title_label)

        # 应用介绍
        self.intro_label = QLabel(
            """
            Make self-reflection as easy and natural as chatting with a friend.<br><br> \
            Choose a review type and start your journey now!"""
        )
        self.intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.intro_label.setStyleSheet(
            """
            QLabel {
                font-size: 15px;
                color: #000000;
            }
        """
        )
        # self.intro_label.setWordWrap(True)
        self.intro_layout.addWidget(self.intro_label)

        # 选择任务类型
        self.task_layout = QGridLayout()
        self.task_layout.setContentsMargins(50, 0, 50, 0)
        self.task_layout.setVerticalSpacing(10)
        self.task_layout.setHorizontalSpacing(10)

        # self.task_label = QLabel("Task")
        # self.task_label.setStyleSheet(
        #     """
        #     QLabel {
        #         font-size: 15px;
        #         color: #000000;
        #     }
        # """
        # )
        # self.task_layout.addWidget(self.task_label, 0, 0, Qt.AlignmentFlag.AlignRight)
        arrow_image_path = os.path.join(basedir, "assets", "down_arrow.png")
        print(arrow_image_path)
        arrow_image_url = QUrl.fromLocalFile(arrow_image_path).toString()
        print(arrow_image_url)

        combo_style = f"""
            QComboBox {{
                background-color: #F7EFE5;
                border: 1px solid #C3ACD0;
                border-radius: 5px;
                color: #000000;
            }}
            QComboBox::drop-down {{
                background-color: #7743DB;
                border-radius: 2.5px;
                width: 24px;
            }}
            QComboBox::down-arrow {{
                image: url({arrow_image_url});
            }}
            QComboBox QAbstractItemView {{
                border-radius: 0px;
                border: 1px solid #FFFBF5;
                background-color: #FFFBF5;
                selection-background-color: #F7EFE5;
            }}
        """

        self.task_combo = QComboBox()
        self.task_combo.addItems(["Review"])
        self.task_combo.setCurrentIndex(0)
        self.task_combo.setFixedSize(120, 25)
        self.task_combo.setStyleSheet(combo_style)
        self.task_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_layout.addWidget(self.task_combo, 0, 0, Qt.AlignmentFlag.AlignCenter)

        # self.type_label = QLabel("Type")
        # self.type_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        # self.type_label.setStyleSheet(
        #     """
        #     QLabel {
        #         font-size: 15px;
        #         color: #000000;
        #     }
        # """
        # )
        # self.task_layout.addWidget(self.type_label, 1, 0, Qt.AlignmentFlag.AlignRight)

        self.type_combo = QComboBox()
        self.type_combo.addItems(["Daily", "Weekly", "Monthly", "Yearly"])
        self.type_combo.setCurrentIndex(0)
        self.type_combo.setFixedSize(120, 25)
        self.type_combo.setStyleSheet(combo_style)
        self.type_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_layout.addWidget(self.type_combo, 1, 0, Qt.AlignmentFlag.AlignCenter)

        self.template_combo = QComboBox()
        self.template_combo.addItems(["Default"])
        self.template_combo.setCurrentIndex(0)
        self.template_combo.setFixedSize(120, 25)
        self.template_combo.setStyleSheet(combo_style)
        self.template_combo.setCursor(Qt.CursorShape.PointingHandCursor)
        self.task_layout.addWidget(
            self.template_combo, 2, 0, Qt.AlignmentFlag.AlignCenter
        )

        self.button_layout = QHBoxLayout()
        self.button_layout.addStretch(1)

        self.start_button = QPushButton("Start")
        self.start_button.setFixedSize(100, 40)
        self.start_button.setStyleSheet(
            """
            QPushButton {
                font-size: 15px;
                color: #FFFBF5;
                border-radius: 5px;
                border: 1px solid #C3ACD0;
                background-color: #7743DB; 
            }
            QPushButton:pressed {
                color: #FFFBF5;
                background-color: #C3ACD0;
                border: 1px solid #7743DB;
            }
        """
        )
        self.start_button.setCursor(Qt.CursorShape.PointingHandCursor)
        self.start_button.clicked.connect(self.on_start_button_clicked)
        self.button_layout.addWidget(self.start_button)
        self.button_layout.addStretch(1)

        # Add layouts to the main layout
        self.main_layout.addLayout(self.intro_layout)
        self.main_layout.addLayout(self.task_layout)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)

    def on_start_button_clicked(self):
        # TODO: Check if the user has set settings
        # TODO: If not, show the settings window
        # Get the task, type and template from the combo box
        self.get_task()
        self.get_type()
        self.get_template()
        # Reload the main window UI to ChatUI
        self.switch_to_chat()
        # TODO: Invoke LLM to start the review

        print("Start button clicked")

    def get_task(self):
        print(self.task_combo.currentText())
        # return self.task_combo.currentText()

    def get_type(self):
        print(self.type_combo.currentText())
        # return self.type_combo.currentText()

    def get_template(self):
        print(self.template_combo.currentText())
        # return self.template_combo.currentText()

    def switch_to_chat(self):
        self.ui_manager.show_chat_ui()
