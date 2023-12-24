import sys
import datetime
import time
import threading
import io
from PyQt6.QtCore import Qt, QUrl, QObject, QThread, pyqtSignal
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
)
from PyQt6.QtGui import QDesktopServices, QAction
from pydub import AudioSegment
from pydub.playback import play

from utils import settings, llm, voice
from utils.settings import SettingsDialog
from utils.voice import TextToSpeechThread


class ChatBackend(QObject):
    text_updated = pyqtSignal(str)

    def receive_text(self, text):
        # 发射文本更新的信号
        self.text_updated.emit(text)


class ReflectionThread(QThread):
    update_text_signal = pyqtSignal(str)

    def __init__(self, assistant, chat_backend):
        QThread.__init__(self)
        self.assistant = assistant
        self.chat_backend = chat_backend

    def run(self):
        # 在后台线程中执行耗时操作
        self.assistant.initialize_session(self.assistant.thread_id)


class Assistant:
    def __init__(self, chat_backend, start_tts_signal):
        self.chat_backend = chat_backend
        self.start_tts_signal = start_tts_signal
        self.user_name = settings.get_user_name()
        self.save_path = settings.get_save_path()
        self.thread_id = llm.create_thread()
        today = datetime.datetime.now()
        self.year_number = today.isocalendar()[0]
        self.week_number = today.isocalendar()[1]
        self.timestamp = today.strftime("%Y%m%d%H%M%S")
        self.title = f"{self.timestamp}-{self.year_number}w{self.week_number}"

        self.chatlog_path = f"{self.save_path}/{self.title}-chatlog.md"
        self.report_path = f"{self.save_path}/{self.title}-report.md"

    def send_to_gui(self, text):
        """将文本发送到GUI"""
        self.chat_backend.receive_text(text)

    def initialize_session(self, thread_id):
        self.send_to_gui("准备复盘...")
        user_message = f"用户称呼：{self.user_name}"
        print(user_message)
        self.chat_with_assistant(user_message, thread_id)
        print("对话初始化完成")
        with open(self.chatlog_path, "w") as file:
            file.write(f"# Weekly Review {self.year_number}{self.week_number}\n\n")
            file.write(f"> Created by {self.user_name} on {self.timestamp}\n\n")

    def chat_with_assistant(self, user_message, thread_id):
        assistant_id = "asst_40vLVijSiJ0cRONnIFPOaeas"
        message = llm.create_message(user_message, thread_id)
        run_id = llm.run_thread(thread_id, assistant_id)
        print("正在与智能助手对话...")

        status = None
        while status != "completed":
            status = llm.check_run_status(thread_id, run_id)
            time.sleep(0.5)
            if status == "failed":
                break

        if status == "completed":
            print("对话完成")
            messages = llm.retrieve_message_list(thread_id)
            response = messages[0].content[0].text.value
            print(response)
            # voice.transcribe_text_to_speech(response)
            self.start_tts_signal.emit(response)
            self.send_to_gui(response)

    def save_chatlog(self, thread_id):
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        messages = llm.retrieve_message_list(thread_id)
        messages = reversed(messages)
        with open(self.chatlog_path, "a") as f:
            f.write("## 对话记录\n\n")

            for i in messages:
                role = i.role
                text = i.content[0].text.value
                if role == "assistant":
                    f.write(f"**Echo**: {text}\n\n")
                else:
                    f.write(f"**{self.user_name}**: {text}\n\n")

            f.write("---\n\n")
            f.write("对话记录生成于： " + timestamp + "\n\n")
        self.send_to_gui("对话记录已保存，正在生成周复盘报告...")

    def generate_report(self, chatlog_path, report_path):
        system_prompt = """你是一个报告写作大师。你的导师要求你写一份周总结。"""
        with open(chatlog_path, "r") as file:
            user_message = file.read()
        response = llm.generate_text_from_oai(system_prompt, user_message)
        with open(report_path, "w") as file:
            file.write(response)
        self.send_to_gui("您的周总结成功生成")


class ReflectiveEchoUI(QMainWindow):
    start_tts_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.setWindowTitle("Reflective Echo")
        self.setGeometry(100, 100, 700, 600)
        self.setFixedSize(700, 600)
        self.chat_backend = ChatBackend()
        self.chat_backend.text_updated.connect(self.update_assistant_message)
        self.start_tts_signal.connect(self.start_text_to_speech)
        self.assistant = Assistant(self.chat_backend, self.start_tts_signal)
        self.tts_thread = None
        self.initUI()

        self.reflection_thread = ReflectionThread(self.assistant, self.chat_backend)
        self.reflection_thread.update_text_signal.connect(
            self.chat_backend.receive_text
        )

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
        self.assistant_message.setFixedSize(600, 200)
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

        self.button_start = QPushButton("开始复盘")
        self.button_start.clicked.connect(self.start_reflection)
        self.bottom_speak = QPushButton("🎙️")
        self.bottom_submit = QPushButton("⌨️")
        self.bottom_submit.clicked.connect(self.submit_user_message)
        self.bottom_finish = QPushButton("结束复盘")
        self.bottom_finish.clicked.connect(self.finish_reflection)

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

    def update_assistant_message(self, text):
        # 这是一个槽函数，用来接收新文本并更新assistant_message QLabel
        self.assistant_message.setText(text)

    def start_reflection(self):
        self.reflection_thread.start()

    def start_text_to_speech(self, text):
        # 现在这个方法会启动文本到语音的转换
        if self.tts_thread is not None and self.tts_thread.isRunning():
            self.tts_thread.wait()

        self.tts_thread = TextToSpeechThread(text)
        self.tts_thread.finished_signal.connect(self.play_response_audio)
        self.tts_thread.start()

    def play_response_audio(self, response_content):
        print("⭕️ 开始播放语音...\n\n")
        print("收到信号的数据类型：", type(response_content))
        assert isinstance(response_content, bytes), "Response content must be bytes"
        byte_stream = io.BytesIO(response_content)
        audio = AudioSegment.from_file(byte_stream, format="mp3")
        play(audio)

    def submit_user_message(self):
        user_message = self.user_message.toPlainText()

        self.assistant.chat_with_assistant(user_message, self.assistant.thread_id)
        # ...对user_message进行处理...
        print("用户消息：", user_message)  # 示例：打印用户消息

    def finish_reflection(self):
        self.assistant.save_chatlog(self.assistant.thread_id)
        self.assistant.generate_report(
            self.assistant.chatlog_path, self.assistant.report_path
        )
        completion_message = "周复盘报告已生成，请到文档区查看「对话记录」与「复盘报告」"
        self.update_assistant_message(completion_message)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setApplicationName("ReflectiveEcho")
    ex = ReflectiveEchoUI()
    ex.show()
    sys.exit(app.exec())
