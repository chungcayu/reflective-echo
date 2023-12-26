import json
import time
import hashlib
import hmac
import base64
import pyaudio
import audioop
from PyQt6.QtCore import QThread, pyqtSignal
from websocket import create_connection
from urllib.parse import quote
import threading

from settings_manager import SettingsManager

SILENCE_THRESHOLD = 500  # 调整该值以识别静音
SILENCE_TIME_LIMIT = 3  # 静音时间超过该值（秒）时，停止录音


class SttThread(QThread):
    text_updated_signal = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.settings_manager = SettingsManager()

        self.xf_app_id = self.settings_manager.get_setting("xunfei_app_id")
        self.xf_api_key = self.settings_manager.get_setting("xunfei_api_key")
        self.running = False

    def run(self):
        self.running = True
        self.client = STTClient(
            self.xf_app_id, self.xf_api_key, self.text_updated_signal
        )
        self.client.start()
        self.running = False

    def stop(self):
        self.running = False
        if self.client:
            self.client.close()


class STTClient:
    def __init__(self, app_id, api_key, text_updated_signal):
        self.text_updated_signal = text_updated_signal

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
            self.text_updated_signal.emit(self.current_text)  # 发出信号
            self.user_message += self.current_text  # 累加结果
            self.final_result_received = False  # 重置标记位

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
