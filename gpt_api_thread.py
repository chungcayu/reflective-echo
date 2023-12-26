# gpt_api_thread.py

from openai import OpenAI
from PyQt6.QtCore import QThread, pyqtSignal
from settings_manager import SettingsManager
import time


class GptApiThread(QThread):
    response_signal = pyqtSignal(str)
    # start_processing_signal = pyqtSignal(str)
    new_user_message_signal = pyqtSignal(str)

    def __init__(self, user_name):
        super().__init__()
        settings_manager = SettingsManager()
        openai_api_key = settings_manager.get_setting("openai_api_key")
        self.client = OpenAI(api_key=openai_api_key)

        self.assistant_id = "asst_40vLVijSiJ0cRONnIFPOaeas"
        self.thread_id = self.create_thread()
        self.user_name = user_name
        self.user_message = None
        # self.start_processing_signal.connect(self.chat_with_assistant)
        self.new_user_message_signal.connect(self.handle_new_user_message)

    def run(self):
        self.initialize_session()

    # Create a thread
    def create_thread(self):
        thread = self.client.beta.threads.create()
        return thread.id

    # Creata a message
    def create_message(self, prompt, thread_id):
        message = self.client.beta.threads.messages.create(
            thread_id=thread_id,
            role="user",
            content=prompt,
        )
        return message

    # Run the assistant
    def run_thread(self, thread_id, assistant_id):
        run = self.client.beta.threads.runs.create(
            thread_id=thread_id,
            assistant_id=assistant_id,
        )
        return run.id

    # Check the status of the run
    def check_run_status(self, thread_id, run_id):
        run_list = self.client.beta.threads.runs.retrieve(
            thread_id=thread_id,
            run_id=run_id,
        )
        return run_list.status

    def retrieve_message_list(self, thread_id):
        messages = self.client.beta.threads.messages.list(
            thread_id=thread_id,
        )
        return messages.data

    def initialize_session(self):
        # 初始化会话
        user_message = f"用户称呼：{self.user_name}"
        self.chat_with_assistant(user_message)

    def handle_new_user_message(self, user_message):
        # 处理新的用户输入
        self.chat_with_assistant(user_message)

    def chat_with_assistant(self, user_message):
        # 与助手对话的代码
        self.user_message = user_message
        self.create_message(self.user_message, self.thread_id)
        self.run_id = self.run_thread(self.thread_id, self.assistant_id)
        self.status = self.check_run_status(self.thread_id, self.run_id)

        while self.status != "completed":
            time.sleep(0.5)
            self.status = self.check_run_status(self.thread_id, self.run_id)
            if self.status == "failed":
                break

        # 如果线程完成，则获取消息
        if self.status == "completed":
            self.messages = self.retrieve_message_list(self.thread_id)
            response = self.messages[0].content[0].text.value

            # 发出带有API响应的信号
            self.response_signal.emit(response)
