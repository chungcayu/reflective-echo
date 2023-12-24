# chat.py

from PyQt6.QtCore import pyqtSignal, QObject

# 1. ✅ 获取用户基本信息


user_name = settings.get_user_name()
save_path = settings.get_save_path()

today = datetime.now()
year_number = today.isocalendar()[0]
week_number = today.isocalendar()[1]
title = f"{year_number}{week_number}"

timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
chatlog_path = f"{save_path}/{title}-wr-chatlog.md"
report_path = f"{save_path}/{title}-wr-report.md"


def initialze_session():
    """初始化对话"""
    print("准备复盘...")
    thread_id = llm.create_thread()
    user_message = f"用户称呼：{user_name}"
    chat_with_assistant(user_message, thread_id)

    with open(chatlog_path, "w") as file:
        file.write(f"# Weekly Review {year_number}{week_number}\n\n")
        file.write(f"- Created by {user_name} on {timestamp}\n\n")
    return thread_id


def chat_with_assistant(user_message, thread_id):
    """与智能助手对话"""
    assistant_id = "asst_40vLVijSiJ0cRONnIFPOaeas"
    message = llm.create_message(user_message, thread_id)
    run_id = llm.run_thread(thread_id, assistant_id)

    status = None
    while status != "completed":
        status = llm.check_run_status(thread_id, run_id)
        # print(f"{status}\r", end="")
        time.sleep(0.5)
        status = status
        if status == "failed":
            status = llm.check_run_status(thread_id, run_id)

    messages = llm.retrieve_message_list(thread_id)

    response = messages[0].content[0].text.value
    role = messages[0].role
    voice.transcribe_text_to_speech(response)  # 播放智能助手回答
    print(response)


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
                f.write(f"**Echo**: {text}\n\n")
                print(f"Echo: {text}\n\n")
            else:
                f.write(f"**{user}**: {text}\n\n")
                print(f"{user}: {text}\n\n")

        f.write("---\n\n")
        f.write("对话记录生成于： " + timestamp + "\n\n")


def genterate_report(chatlog_path, report_path):
    pass



thread_id = initialze_session()
# print(thread_id)


# # 3. 获取用户文本输入


while True:
    # print("\n你可以选择输入文本，或语音对话。输入s保存文件\n\n")
    print("- 🎙️：输入「t」，开始语音对话")
    print("- 🎹：输入文本，开始对话")
    print("- 💾：输入「s」，结束对话，保存文件\n\n")

    user_message = input("You: ").lower()

    # 用户选择语音输入
    if user_message == "t":
        user_message = voice.transcribe_speech_to_text()  # 用户语音输入，讯飞语音转文本，返回文本
        chat_with_assistant(user_message, thread_id)

    # 用户选择结束对话，获取大纲，程序终止
    elif user_message == "s":
        print("文书大纲已生成，请到文档区查看「对话记录」与「文书大纲」\n\n")
        # utils.save_chatlog(chatlog_path, thread_id, user_name)
        # genterate_report(chatlog_path, report_path)
        break

    # 用户选择文本输入
    else:
        chat_with_assistant(user_message, thread_id)
