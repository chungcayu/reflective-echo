from PyQt6.QtWidgets import (
    QApplication,
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QTextEdit,
    QPushButton,
    QLabel,
    QLineEdit,
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QPixmap


class MessageUI(QWidget):
    def __init__(self, text, is_assistant=True):
        super().__init__()
        msg_layout = QHBoxLayout()

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

        assistant_msg_label = QLabel(text)
        assistant_msg_label.setWordWrap(True)

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

        user_msg_label = QLabel(text)
        user_msg_label.setWordWrap(True)

        if is_assistant:
            msg_layout.addWidget(assistant_avatar)
            msg_layout.addWidget(assistant_msg_label, 1)
            msg_layout.setAlignment(Qt.AlignmentFlag.AlignLeft)
        else:
            msg_layout.addWidget(user_msg_label, 1)
            msg_layout.addWidget(user_avatar)
            msg_layout.setAlignment(Qt.AlignmentFlag.AlignRight)

        self.setLayout(msg_layout)


class ChatUI(QWidget):
    def __init__(self):
        super().__init__()
        layout = QVBoxLayout()

        # 欢迎信息
        self.messages_area = QVBoxLayout()
        welcome_message = MessageUI("正在准备中...")
        self.messages_area.addWidget(welcome_message)

        # 输入区域
        input_area = QHBoxLayout()
        self.input_field = QLineEdit()
        self.send_button = QPushButton("✅")
        self.voice_button = QPushButton("🎙️")
        input_area.addWidget(self.input_field, 1)
        input_area.addWidget(self.send_button)
        input_area.addWidget(self.voice_button)

        # 组合布局
        layout.addLayout(self.messages_area, 1)
        layout.addLayout(input_area)
        self.setLayout(layout)

        # 信号连接
        self.send_button.clicked.connect(self.send_message)

    def send_message(self):
        # 获取输入文本并清除输入框
        text = self.input_field.text()
        self.input_field.clear()

        # 创建新的消息框并添加到界面
        if text:
            user_message = MessageUI(text, is_assistant=False)
            self.messages_area.addWidget(user_message)


if __name__ == "__main__":
    app = QApplication([])
    chat_ui = ChatUI()
    chat_ui.show()
    app.exec()
