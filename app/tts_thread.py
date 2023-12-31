import base64
import io
import json
import uuid
import requests
from requests.exceptions import RequestException, HTTPError, ConnectionError, Timeout
from PyQt6.QtCore import QThread, pyqtSignal
from pydub import AudioSegment
from pydub.playback import play

from settings_manager import SettingsManager

import logging

logger = logging.getLogger(__name__)


class TtsThread(QThread):
    finished_signal = pyqtSignal()
    errorOccurred = pyqtSignal(str, str)

    def __init__(self, text):
        super().__init__()
        self.settings_manager = SettingsManager()
        try:
            self.mm_group_id = self.settings_manager.get_setting("minimax_group_id")
            self.mm_api_key = self.settings_manager.get_setting("minimax_api_key")
            self.vol_appid = self.settings_manager.get_setting("volcano_app_id")
            self.vol_access_token = self.settings_manager.get_setting(
                "volcano_access_token"
            )

            logger.info("Successfully loaded minimax API keys from settings")
        except Exception as e:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 获取MiniMax API密钥时出现异常: {e}")
            self.errorOccurred.emit("获取MiniMax API密钥时出现异常", str(e))
            return

        self.text = text

    def run(self):
        # 获取音频数据
        # audio_data = self.minimax_tts(self.text)
        audio_data = self.volcano_tts(self.text)
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
                    logger.exception("❗️Error occurred")
                    return None

            if "audio/mpeg" in response.headers.get("Content-Type", ""):
                print("✅ 调用成功")
                return response.content
            else:
                print("⚠️ 响应的内容类型不符合预期。")
                return None

        except HTTPError as http_err:
            logger.exception("❗️Error occurred")
            print(f"⚠️ HTTP错误: {http_err}")
        except ConnectionError as conn_err:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 连接错误: {conn_err}")
        except Timeout as timeout_err:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 请求超时: {timeout_err}")
        except RequestException as req_err:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 请求异常: {req_err}")
        return None

    def volcano_tts(self, text):
        print("⭕️ 开始调用Volcano API...")
        voice_type = "BV700_V2_streaming"
        vol_cluster = "volcano_tts"
        api_url = "https://openspeech.bytedance.com/api/v1/tts"
        header = {"Authorization": f"Bearer;{self.vol_access_token}"}
        request_json = {
            "app": {
                "appid": self.vol_appid,
                "token": "access_token",
                "cluster": vol_cluster,
            },
            "user": {"uid": "388808087185088"},
            "audio": {
                "voice_type": voice_type,
                "encoding": "mp3",
                "speed_ratio": 1.0,
                "volume_ratio": 1.0,
                "pitch_ratio": 1.0,
            },
            "request": {
                "reqid": str(uuid.uuid4()),
                "text": text,
                "text_type": "plain",
                "operation": "query",
                "with_frontend": 1,
                "frontend_type": "unitTson",
            },
        }
        try:
            resp = requests.post(api_url, json.dumps(request_json), headers=header)
            if resp.status_code == 200:
                resp_code = resp.json()["code"]
                if resp_code == 3000:
                    print("✅ 调用成功")
                    data = resp.json()["data"]
                    response = base64.b64decode(data)
                    return response
                elif resp_code == 3001:
                    print(f"⚠️ 语音合成失败，错误代码：{resp_code}")
                    print(resp.json()["message"])
                    return None
                else:
                    print(f"⚠️ 语音合成失败，错误代码：{resp_code}")
                    print(resp.json()["message"])
                    return None

        except Exception as e:
            e.with_traceback()

    def play_audio(self, audio_data):
        """播放音频数据"""
        try:
            print("⭕️ 开始播放语音...")
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
            play(audio_segment)
        except Exception as e:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 播放语音时出现异常: {e}")
