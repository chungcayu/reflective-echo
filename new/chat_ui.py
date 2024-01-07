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
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap


class MessageUI(QWidget):
    def __init__(self, text, is_assistant=True):
        super().__init__()

        msg_layout = QHBoxLayout()
        msg_layout.setContentsMargins(0, 0, 0, 0)
        msg_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

        assistant_avatar = QLabel()
        assistant_pixmap = QPixmap("assets/echo_avatar.png")
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
                max-height: 25px;
                padding: 5px;
            }
        """
        )

        user_avatar = QLabel()
        user_pixmap = QPixmap("assets/user_avatar.png")
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
                min-height: 25px;
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
    def __init__(self):
        super().__init__()
        self.initUI()
        self.initialize()

    def initUI(self):
        self.main_layout = QVBoxLayout()
        self.main_layout.setContentsMargins(20, 20, 20, 20)
        self.main_layout.setSpacing(10)

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

        # # 默认初始化消息
        # assistant_default_msg = MessageUI("正在准备中...")
        # self.msg_display_layout.addWidget(assistant_default_msg)

        # 将滚动区域添加到主布局
        self.main_layout.addWidget(self.scroll_area, 1)

        input_layout = QHBoxLayout()

        self.input_field = QTextEdit()
        self.input_field.setStyleSheet(
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
        input_layout.addWidget(self.input_field)

        button_layout = QHBoxLayout()
        button_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.voice_button = QPushButton("🎙️")
        self.voice_button.setFixedSize(40, 40)
        self.voice_button.clicked.connect(self.on_voice_button_clicked)

        self.send_button = QPushButton("✅")
        self.send_button.setFixedSize(40, 40)
        self.send_button.clicked.connect(self.on_send_button_clicked)

        button_layout.addWidget(self.voice_button)
        button_layout.addWidget(self.send_button)

        # 组合布局
        self.main_layout.addLayout(input_layout)
        self.main_layout.addLayout(button_layout)
        self.setLayout(self.main_layout)

    def initialize(self):
        # 初始化消息
        assistant_default_msg = MessageUI("正在准备中...")
        self.msg_display_layout.addWidget(assistant_default_msg)
        self.msg_display_layout.addStretch(1)

    def send_msg_to_display(self):
        # 获取输入文本并清除输入框
        text = self.input_field.toPlainText()
        self.input_field.clear()

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
        pass

    def on_send_button_clicked(self):
        self.send_msg_to_display()


if __name__ == "__main__":
    app = QApplication([])
    chat_ui = ChatUI()
    chat_ui.show()
    app.exec()
