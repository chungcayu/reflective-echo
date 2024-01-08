import base64
import io
import json
import uuid
import requests
import time
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

    def volcano_tts_short(self, text):
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

    def submit_task_tts(self, text):
        """发送请求，输入文本，返回任务ID和任务状态"""
        print("⭕️ 正在提交任务...")

        voice_type = "BV700_V2_streaming"
        url = "https://openspeech.bytedance.com/api/v1/tts_async/submit"
        headers = {
            "Authorization": f"Bearer; {self.vol_access_token}",
            "Content-Type": "application/json",
            "Resource-Id": "volc.tts_async.default",
        }
        payload = {
            "appid": self.vol_appid,
            "text": text,
            "format": "mp3",
            "voice_type": voice_type,
            "sentence_interval": 500,
        }

        try:
            response = requests.post(url, headers=headers, data=json.dumps(payload))

            # Check for successful request
            if response.status_code == 200:
                response = response.json()
                task_id = response.get("task_id")
                task_status = response.get("task_status")
                print(f"Processing task: {task_id}, its status: {task_status}")
                return task_id, task_status
            else:
                raise Exception(f"Error: {response.status_code} - {response.text}")

        except requests.exceptions.RequestException as e:
            # Handle any errors related to the requests library
            print(f"RequestException occurred: {e}")
            # Depending on the situation, you may want to log the error, retry the request, etc.
        except ValueError as ve:
            # Handle missing task_id or task_status
            print(f"ValueError: {ve}")
        except Exception as other_exception:
            # Make sure to handle any other exception that is not caught by specific except blocks
            print(f"An unexpected error occurred: {other_exception}")

    def get_audio_url(self, task_id, task_status):
        print("⭕️ 正在获取链接...")
        """发送请求，输入任务ID和状态，返回语音URL"""

        url = f"https://openspeech.bytedance.com/api/v1/tts_async/query"
        headers = {
            "Authorization": f"Bearer; {self.vol_access_token}",
            "Content-Type": "application/json",
            "Resource-Id": "volc.tts_async.default",
        }
        q_params = {"appid": self.vol_appid, "task_id": task_id}

        try:
            while task_status == 0:
                time.sleep(0.5)
                response = requests.get(url, headers=headers, params=q_params)
                if response.status_code == 200:
                    response = response.json()
                    task_status = response.get("task_status")
                    if task_status is None:
                        raise ValueError("Missing 'task_status' in response.")
                else:
                    raise Exception(
                        f"Error: Unsuccessful status code {response.status_code} - {response.text}"
                    )

            if task_status == 1:
                audio_url = response.get("audio_url")
                if not audio_url:
                    raise ValueError("Missing 'audio_url' in response.")
                return audio_url
            else:
                raise Exception(
                    "Error: Unsuccessful task status - the task did not complete successfully."
                )

        except requests.exceptions.RequestException as e:
            print(f"RequestException occurred: {e}")
            # Depending on the situation, proper error handling code would go here.
            # That might involve logging the error, retrying the request, or raising an exception.
        except ValueError as ve:
            print(f"ValueError: {ve}")
            # Handle missing data in the response.
        except Exception as ex:
            print(f"An unexpected error occurred: {ex}")
            # Handle other unforeseen errors.

    def volcano_tts(self, text):
        """调用火山引擎API，输入文本，返回语音URL"""
        print("⭕️ 开始调用Volcano API...")
        task_id, task_status = self.submit_task_tts(text)
        audio_url = self.get_audio_url(task_id, task_status)
        print(f"Audio url: {audio_url}")
        print("⭕️ 正在获取语音文件...")
        try:
            response = requests.get(audio_url)
            return response.content
        except requests.exceptions.RequestException as e:
            print(f"RequestException occurred: {e}")
        return response

    def play_audio(self, audio_data):
        """播放音频数据"""
        try:
            print("⭕️ 开始播放语音...")
            audio_segment = AudioSegment.from_file(io.BytesIO(audio_data), format="mp3")
            play(audio_segment)
        except Exception as e:
            logger.exception("❗️Error occurred")
            print(f"⚠️ 播放语音时出现异常: {e}")
