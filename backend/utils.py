import io
import datetime
import time
import os
from dotenv import load_dotenv
from pydub import AudioSegment
from pydub.playback import play
import speech_recognition as sr

import llm
from voice import huoshan_tts, xunfei_stt

load_dotenv()


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
    response = huoshan_tts(text)
    # response = minimax_tts(text)
    # response = openai_tts(text)
    print("⭕️ 开始播放语音...\n\n")
    play_response_audio(response)


def transcribe_speech_to_text():
    text = xunfei_stt()
    return text


def create_file_names(username):
    current_date = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
    chatlog = f"data/{current_date}-{username}-chatlog.md"
    outline = f"data/{current_date}-{username}-outline.md"
    return chatlog, outline


def chat_with_mentor(user_message, thread_id, assistant_id):
    message = llm.create_message(user_message, thread_id)
    run_id = llm.run_thread(thread_id, assistant_id)
    print(f"Your new run id is... {run_id}\n\n")  # debug

    status = None
    while status != "completed":
        status = llm.check_run_status(thread_id, run_id)
        print(f"{status}\r", end="")
        time.sleep(0.5)
        status = status
        if status == "failed":
            status = llm.check_run_status(thread_id, run_id)

    messages = llm.retrieve_message_list(thread_id)
    # print(f"Messages: {messages}\n\n")

    response = messages[0].content[0].text.value
    role = messages[0].role
    print("⭕️ 开始语音转换...\n\n")
    transcribe_text_to_speech(response)  # 播放智能助手回答
    print(f"{'导师' if role == 'assistant' else 'User'}: {response}\n\n")


def create_session():
    """创建会话"""
    thread_id = llm.create_thread()
    assistant_id = llm.get_assistant_id()
    print("✅ 成功创建会话\n\n")
    return thread_id, assistant_id


def initialze_chatlog(chatlog_path, user, user_id, thread_id):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    with open(chatlog_path, "w") as file:
        file.write(f"# {user}的对话记录\n\n")
        file.write(f"## 元信息\n\n")
        file.write(f"- User ID：{user_id}\n")
        file.write(f"- Thread ID：{thread_id}\n")
        file.write(f"- Start Time：{timestamp}\n\n")
    print("✅ 成功创建档案\n\n")


def save_chatlog(chatlog_path, thread_id, user):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    messages = llm.retrieve_message_list(thread_id)
    messages = reversed(messages)
    with open(chatlog_path, "a") as f:
        f.write("## 对话记录\n\n")

        for i in messages:
            role = i.role
            text = i.content[0].text.value
            if role == "assistant":
                f.write(f"**导师**: {text}\n\n")
                print(f"导师: {text}\n\n")
            else:
                f.write(f"**{user}**: {text}\n\n")
                print(f"{user}: {text}\n\n")

        f.write("---\n\n")
        f.write("对话记录生成于： " + timestamp + "\n\n")
