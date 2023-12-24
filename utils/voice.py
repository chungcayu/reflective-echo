# voice.py

import base64
import datetime
import hashlib
import hmac
import io
import json
import logging
import os
import threading
import time
import requests
from socket import create_connection
from urllib.parse import quote

import audioop
import pyaudio
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr
from websocket import create_connection, WebSocketConnectionClosedException

from .settings import get_api_key

# hs_app_id = get_api_key("huoshan_app_id")
# hs_access_token = get_api_key("huoshan_access_token")
# hs_cluster_id = get_api_key("huoshan_cluster_id")
xf_app_id = get_api_key("xunfei_app_id")
xf_api_key = get_api_key("xunfei_api_key")
mm_group_id = get_api_key("minimax_group_id")
mm_api_key = get_api_key("minimax_api_key")


"""
MiniMax API
"""

mm_voice_id = "male-qn-qingse"


def minimax_tts(text):
    """调用MiniMax API，输入文本，返回语音文件"""
    url = f"https://api.minimax.chat/v1/text_to_speech?GroupId={mm_group_id}"
    headers = {
        "Authorization": f"Bearer {mm_api_key}",
        "Content-Type": "application/json",
    }
    data = {
        "voice_id": mm_voice_id,
        "text": text,
        "model": "speech-01",
        "speed": 1.0,
        "vol": 1.0,
        "pitch": 0,
    }
    response = requests.post(url, headers=headers, json=data)
    print("trace_id", response.headers.get("Trace-Id"))
    if response.status_code != 200 or "json" in response.headers["Content-Type"]:
        print("调用失败", response.status_code, response.text)
        exit()
    return response.content


"""
火山引擎 API
"""

# 选择音色：灿灿 2.0：BV700_V2_streaming ｜ 超自然音色-梓梓  BV406_streaming | 超自然音色-梓梓2.0：BV406_V2_streaming ｜ 超自然音色-燃燃2.0：BV407_V2_streaming
hs_voice_type = "0：BV700_V2_streaming"


def submit_task_text_to_speech(text):
    """发送请求，输入文本，返回任务ID和任务状态"""

    print("⭕️ 正在提交任务...")
    url = "https://openspeech.bytedance.com/api/v1/tts_async/submit"
    headers = {
        "Authorization": f"Bearer; {hs_access_token}",
        "Content-Type": "application/json",
        "Resource-Id": "volc.tts_async.default",
    }
    payload = {
        "appid": hs_app_id,
        "text": text,
        "format": "mp3",
        "voice_type": hs_voice_type,
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


def get_audio_url(task_id, task_status):
    print("⭕️ 正在获取链接...")
    """发送请求，输入任务ID和状态，返回语音URL"""

    base_url = f"https://openspeech.bytedance.com/api/v1/tts_async/query"

    headers = {
        "Authorization": f"Bearer; {hs_access_token}",
        "Content-Type": "application/json",
        "Resource-Id": "volc.tts_async.default",
    }

    q_params = {"appid": hs_app_id, "task_id": task_id}

    try:
        while task_status == 0:
            time.sleep(0.5)
            response = requests.get(base_url, headers=headers, params=q_params)
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


def get_audio_response(audio_url):
    """输入语音URL，返回语音文件"""
    print("⭕️ 正在获取语音文件...")
    try:
        response = requests.get(audio_url)
        return response.content
    except requests.exceptions.RequestException as e:
        print(f"RequestException occurred: {e}")


def huoshan_tts(text):
    """调用火山引擎API，输入文本，返回语音URL"""
    # print("Submitting task...\n")
    task_id, task_status = submit_task_text_to_speech(text)
    # print("Submitted successfully, transcribing text to speech...\n")
    audio_url = get_audio_url(task_id, task_status)
    # print(f"Audio url: {audio_url}")
    response = get_audio_response(audio_url)
    return response


"""
讯飞 API
"""


SILENCE_THRESHOLD = 500  # 设置为合适的静音阈值，这个值可能需要根据实际情况调整
SILENCE_TIME_LIMIT = 2  # 静音时间阈值设置为2秒钟


class STTClient:
    def __init__(self, app_id, api_key):
        base_url = "ws://rtasr.xfyun.cn/v1/ws"
        ts = str(int(time.time()))
        tt = (app_id + ts).encode("utf-8")
        md5 = hashlib.md5()
        md5.update(tt)
        baseString = md5.hexdigest()
        baseString = bytes(baseString, encoding="utf-8")

        apiKey = api_key.encode("utf-8")
        signa = hmac.new(apiKey, baseString, hashlib.sha1).digest()
        signa = base64.b64encode(signa)
        signa = str(signa, "utf-8")
        self.end_tag = '{"end": true}'
        self.current_text = ""  # 状态变量，用于存储当前已接收的文本
        self.final_result_received = False  # 状态标记，表示是否接收到最终结果
        self.user_message = ""  # 存储用户的消息
        self.last_active_time = time.time()  # 记录上一次检测到声音的时间

        # Adding print for debugging
        # print(f"Trying to connect to {base_url}?appid={app_id}&ts={ts}&signa={quote(signa)}")

        try:
            self.ws = create_connection(
                base_url + "?appid=" + app_id + "&ts=" + ts + "&signa=" + quote(signa)
            )
        except Exception as e:
            # Adding error handling and print
            print("Failed to create WebSocket connection: " + str(e))
            return
        else:
            self.trecv = threading.Thread(target=self.recv)
            self.trecv.start()

    def start(self):
        t1 = threading.Thread(target=self.send)
        t2 = threading.Thread(target=self.recv)
        t1.start()
        t2.start()
        t1.join()
        self.close()
        t2.join()

    def send(self):
        rate = 16000  # 采样率
        format = pyaudio.paInt16  # 采样深度
        channels = 1  # 单声道
        chunk = 1280  # 每次读取的音频流长度
        p = pyaudio.PyAudio()
        stream = p.open(
            rate=rate,
            format=format,
            channels=channels,
            input=True,
            frames_per_buffer=chunk,
        )

        print("----> 导师正在倾听，请讲述你的想法\n\n")

        last_sound_detected_time = time.time()  # 初始化最后声音检测时间

        while True:
            data = stream.read(chunk)
            # 计算当前音频块的音量能量
            audio_energy = audioop.rms(data, 2)  # 音频能量检测，2表示采样深度为2bytes

            if audio_energy < SILENCE_THRESHOLD:  # 判断当前块是否为静音
                current_time = time.time()
                if current_time - last_sound_detected_time > SILENCE_TIME_LIMIT:
                    # print(f"\n静音时间超过{SILENCE_TIME_LIMIT}秒，停止录音")
                    print("\n\n----> 导师正在思考，请稍等\n\n")
                    break  # 静音超过了设定的阈值，退出循环，结束发送音频数据
            else:
                last_sound_detected_time = time.time()  # 如果检测到声音，更新最后的声音检测时间

            self.ws.send(data)  # 将音频数据发送到WebSocket
        stream.stop_stream()  # 停止音频流
        stream.close()  # 关闭音频流
        p.terminate()  # 结束pyaudio会话

    def on_message(self, message):
        try:
            result_dict = json.loads(message)
        except Exception as e:
            print("Error parsing the JSON message: ", e)
            return

        if result_dict["action"] == "started":
            # print("握手成功")
            self.current_text = ""  # 重置文本状态
            self.final_result_received = False  # 重置标记位

        if result_dict["action"] == "result":
            data = json.loads(result_dict["data"])
            result = data["cn"]["st"]["rt"]
            result_type = data["cn"]["st"]["type"]

            if result_type == "0":
                self.final_result_received = True

            new_text = ""
            for i in result:
                for x in i["ws"]:
                    w = x["cw"][0]["w"]
                    wp = x["cw"][0]["wp"]
                    if wp != "s":
                        new_text += w

            if not self.final_result_received:  # 如果还未接收最终结果，不做输出
                self.current_text = new_text
            else:
                if new_text != self.current_text:
                    self.current_text = new_text  # 更新已存储文本

        # 只有接收到最终结果时才进行输出
        if self.final_result_received:
            print(self.current_text, end="", flush=True)
            self.user_message += self.current_text  # 将结果累加到user_message中
            self.final_result_received = False  # 重置标记位，准备下一次接收

    def recv(self):
        try:
            while self.ws.connected:
                message = self.ws.recv()
                if not message:
                    # print("No more results.")
                    break
                self.on_message(message)
        except Exception as e:
            # print("recv exception:", e)
            return None

    def close(self):
        if self.ws and self.ws.connected:
            self.ws.close()
            # print("Connection closed")


# 实时语音转写
def xunfei_stt():
    logging.basicConfig()
    stt_client = STTClient(xf_app_id, xf_api_key)
    stt_client.start()
    # print("Final transcribed message:", stt_client.user_message)
    return stt_client.user_message


def play_local_audio(path):
    """输入音频本地路径，播放音频"""
    audio = AudioSegment.from_file(path)
    play(audio)


def play_response_audio(response):
    """输入响应对象，播放音频"""
    byte_stream = io.BytesIO(response)
    audio = AudioSegment.from_file(byte_stream, format="mp3")
    play(audio)


def save_audio(file_path, response):
    """保存音频到本地"""
    with open(file_path, "wb") as f:
        f.write(response.content)


def transcribe_text_to_speech(text):
    # response = huoshan_tts(text)
    response = minimax_tts(text)
    # response = openai_tts(text)
    print("⭕️ 开始播放语音...\n\n")
    play_response_audio(response)


def transcribe_speech_to_text():
    text = xunfei_stt()
    return text
