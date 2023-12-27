import io
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from PyQt6.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from pydub.playback import play

from settings_manager import SettingsManager


class TtsThread(QThread):
    finished_signal = pyqtSignal()
    errorOccurred = pyqtSignal(str, str)

    def __init__(self, text):
        super().__init__()
        self.settings_manager = SettingsManager()
        self.mm_group_id = self.settings_manager.get_setting("minimax_group_id")
        self.mm_api_key = self.settings_manager.get_setting("minimax_api_key")

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
            "voice_id": "male-qn-jingying",
            "text": text,
            "model": "speech-01",
            "speed": 1,
            "vol": 1.0,
            "pitch": 0,
        }
        try:
            response = requests.post(url, headers=headers, json=data, timeout=10)
            response.raise_for_status()  # 检查HTTP响应状态

            if "application/json" in response.headers.get("Content-Type", ""):
                response_data = response.json()

                # 检查API的特定错误代码
                if (
                    response_data.get("base_resp", {}).get("status_code") == 1004
                ):  # 鉴权失败
                    # print("⚠️ API密钥信息可能有误，请检查您的APIKEY。")
                    self.errorOccurred.emit("鉴权失败", "API密钥信息可能有误，请检查您的APIKEY。")
                    return None

            if "audio/mpeg" in response.headers.get("Content-Type", ""):
                print("✅ 调用成功")
                return response.content
            else:
                print("⚠️ 响应的内容类型不符合预期。")
                return None

        except HTTPError as http_err:
            print(f"⚠️ HTTP错误: {http_err}")
        except ConnectionError as conn_err:
            print(f"⚠️ 连接错误: {conn_err}")
        except Timeout as timeout_err:
            print(f"⚠️ 请求超时: {timeout_err}")
        except RequestException as req_err:
            print(f"⚠️ 请求异常: {req_err}")

        return None

    def play_audio(self, audio_data):
        """播放音频数据"""
        print("⭕️ 开始播放语音...")
        audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
        play(audio_segment)
