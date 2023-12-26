import io
import requests
from PyQt6.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from pydub.playback import play

from settings_manager import SettingsManager


class TtsThread(QThread):
    finished_signal = pyqtSignal()

    def __init__(self, text):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.mm_group_id = self.settings_manager.get_setting("mm_group_id")
        self.mm_api_key = self.settings_manager.get_setting("mm_api_key")
        self.mm_voice_id = self.settings_manager.get_setting("mm_voice_id")

        self.text = text

    def run(self):
        # 获取音频数据
        audio_data = self.minimax_tts(self.text)
        if audio_data:
            # 播放音频
            self.play_audio(audio_data)

        # 发出完成信号
        self.finished_signal.emit()

    def minimax_tts(self, text):
        """调用MiniMax API，输入文本，返回语音文件"""
        print("⭕️ 正在调用MiniMax API...")
        url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={self.mm_group_id}"
        headers = {
            "Authorization": f"Bearer {self.mm_api_key}",
            "Content-Type": "application/json",
        }
        data = {
            "voice_id": self.mm_voice_id,
            "text": text,
            "model": "speech-01",
            "speed": 1.0,
            "vol": 1.0,
            "pitch": 0,
        }
        response = requests.post(url, headers=headers, json=data)
        if (
            response.status_code == 200
            and "audio/mpeg" in response.headers["Content-Type"]
        ):
            return response.content
        else:
            print("调用失败", response.status_code, response.text)
            return None

    def play_audio(self, audio_data):
        """播放音频数据"""
        print("⭕️ 开始播放语音...\n\n")
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        play(audio_segment)
