import os
from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QScrollArea,
    QSpacerItem,
    QSizePolicy,
)
from PyQt6.QtCore import Qt, QSize
from PyQt6.QtGui import QIcon, QPixmap, QCursor


basedir = os.path.dirname(__file__)


class MessageUI(QWidget):
    def __init__(self, text, is_assistant=True):
        super().__init__()

        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        assistant_avatar = QLabel()
        assistant_pixmap = QPixmap(os.path.join(basedir, "assets", "echo_avatar.png"))
        assistant_pixmap = assistant_pixmap.scaled(
            40,
            40,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        assistant_avatar.setPixmap(assistant_pixmap)
        assistant_avatar.setFixedSize(40, 40)

        assistant_msg = QTextEdit()
        assistant_msg.insertPlainText(text)
        assistant_msg.setReadOnly(True)
        # #E5E1DA #F7EFE5
        assistant_msg.setStyleSheet(
            """
            QTextEdit {
                background-color: #F7EFE5; 
                color: #000000;
                border-radius: 5px;
                border: none;
                padding: 5px;
            }
        """
        )

        user_avatar = QLabel()
        user_pixmap = QPixmap(os.path.join(basedir, "assets", "user_avatar.png"))
        user_pixmap = user_pixmap.scaled(
            40,
            40,
            Qt.AspectRatioMode.KeepAspectRatio,
            Qt.TransformationMode.SmoothTransformation,
        )
        user_avatar.setPixmap(user_pixmap)
        user_avatar.setFixedSize(40, 40)

        user_msg = QTextEdit()
        user_msg.insertPlainText(text)
        user_msg.setReadOnly(True)
        # #A1EEBD #C3ACD0
        user_msg.setStyleSheet(
            """
            QTextEdit {
                background-color: #C3ACD0;
                color: #000000;
                border-radius: 5px;
                border: none;
                padding: 5px;
            }
        """
        )

        if is_assistant:
            msg_layout.addWidget(assistant_avatar)
            msg_layout.addWidget(assistant_msg)
            msg_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            msg_layout.addWidget(user_msg)
            msg_layout.addWidget(user_avatar)
            msg_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.setLayout(msg_layout)


class ChatUI(QWidget):
    def __init__(self, ui_manager):
        super().__init__()
        self.ui_manager = ui_manager
        self.initUI()
        self.initialize()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

        # 说明区域
        self.intro_label = QLabel("Review - Daily")
        self.intro_label.setStyleSheet(
            """
            QLabel {
                font-size: 14px;
                font-weight: bold;
                color: #000000;
                background-color: #F5F5F5;
                padding: 5px;
                border-radius: 5px;
            }
        """
        )
        self.intro_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.main_layout.addWidget(self.intro_label)

        # 消息显示区域
        # 创建滚动区域
        self.scroll_area = QScrollArea()
        self.scroll_area.setContentsMargins(0, 0, 0, 0)
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setAlignment(Qt.AlignmentFlag.AlignTop)
        self.scroll_area.setStyleSheet(
            """
        QScrollArea {
            border: none;
        }
        QScrollBar:vertical {
            border: none;
            width: 0.5px;
            margin: 0px 0 0px 0;
        }
        QScrollBar::handle:vertical {
            min-height: 0px;
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

        # 用于放置消息的容器
        self.msg_display_widget = QWidget()
        self.msg_display_layout = QVBoxLayout(self.msg_display_widget)
        self.msg_display_layout.setContentsMargins(0, 0, 0, 0)
        self.msg_display_layout.setSpacing(15)  # 设置消息间固定的间距

        # 将消息容器设置为滚动区域的子控件
        self.scroll_area.setWidget(self.msg_display_widget)

        # 将滚动区域添加到主布局
        self.main_layout.addWidget(self.scroll_area, 1)

        # 输入区域
        self.input_area_layout = QHBoxLayout()
        self.input_area_layout.setContentsMargins(0, 0, 0, 0)
        self.input_area_layout.setSpacing(5)

        self.input_edit = QTextEdit()
        self.input_edit.setStyleSheet(
            """
            QTextEdit {
                background-color: #F5F5F5;
                color: #000000;
                border-radius: 5px;
                border: 1px solid #E0E0E0;
                min-height: 20px;
                max-height: 50px;
                padding: 5px;
            }
        """
        )

        button_style = (
            "QPushButton {"
            "   border: none;"
            "   border-radius: 5px;"
            "   background-color: none;"
            "}"
        )

        self.voice_button = QPushButton()
        self.voice_button.setIcon(
            QIcon(os.path.join(basedir, "assets", "mic_button.png"))
        )
        self.voice_button.setIconSize(QSize(20, 20))
        self.voice_button.setFixedSize(QSize(30, 30))
        self.voice_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.voice_button.clicked.connect(self.on_voice_button_clicked)

        self.send_button = QPushButton()
        self.send_button.setIcon(
            QIcon(os.path.join(basedir, "assets", "send_button.png"))
        )
        self.send_button.setIconSize(QSize(20, 20))
        self.send_button.setFixedSize(QSize(30, 30))
        self.send_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.send_button.clicked.connect(self.on_send_button_clicked)

        self.complete_button = QPushButton()
        self.complete_button.setIcon(
            QIcon(os.path.join(basedir, "assets", "complete_button.png"))
        )
        self.complete_button.setIconSize(QSize(20, 20))
        self.complete_button.setFixedSize(QSize(30, 30))
        self.complete_button.setCursor(QCursor(Qt.CursorShape.PointingHandCursor))
        self.complete_button.clicked.connect(self.on_complete_button_clicked)

        self.setStyleSheet(button_style)
        self.input_area_layout.addWidget(self.complete_button)
        self.input_area_layout.addWidget(self.input_edit)
        self.input_area_layout.addWidget(self.voice_button)
        self.input_area_layout.addWidget(self.send_button)

        # 组合布局

        self.main_layout.addLayout(self.input_area_layout)
        self.setLayout(self.main_layout)

    def initialize(self):
        # 初始化消息
        assistant_default_msg = MessageUI("正在准备中...")
        self.msg_display_layout.addWidget(assistant_default_msg)
        self.msg_display_layout.addStretch(1)

    def send_msg_to_display(self):
        # 获取输入文本并清除输入框
        text = self.input_edit.toPlainText()
        self.input_edit.clear()

        # 移除已存在的伸缩量（如果有）
        if self.msg_display_layout.count() > 0:
            item = self.msg_display_layout.takeAt(self.msg_display_layout.count() - 1)
            if item.spacerItem():
                del item

        # 创建新的消息框并添加到界面
        if text:
            user_message = MessageUI(text, is_assistant=False)
            self.msg_display_layout.addWidget(user_message)

        # 滚动到最新的消息
        self.scroll_area.verticalScrollBar().setValue(
            self.scroll_area.verticalScrollBar().maximum()
        )

        self.msg_display_layout.addStretch(1)

    def on_voice_button_clicked(self):
        print("Voice button clicked")

    def on_send_button_clicked(self):
        print("Send button clicked")
        self.send_msg_to_display()

    def on_complete_button_clicked(self):
        print("Complete button clicked")
        self.switch_to_mainwindown()

    def switch_to_mainwindown(self):
        self.ui_manager.show_default_ui()


if __name__ == "__main__":
    app = QApplication([])
    chat_ui = ChatUI()
    chat_ui.show()
    app.exec()
