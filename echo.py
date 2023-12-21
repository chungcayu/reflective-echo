# echo.py
import utils


# 1. 播放欢迎语，系统使用指南
welcome_message_path = "assets/welcome.mp3"
utils.play_local_audio(welcome_message_path)

# 2. 获取用户基本信息
user_name = get_user_name()

# 3. 获取用户文本输入
user_message = get_user_message()

# 3. 基于用户基本信息开启对话
chatlog_path, report_path = utils.create_file_names()
thread_id, assistant_id = utils.create_session()
utils.initialze_chatlog(chatlog_path, user_name, thread_id)

print("✅ 正在开启对话...\n\n")
utils.chat_with_mentor(user_message, thread_id, assistant_id)

# print(thread_id)

while True:
    # print("\n你可以选择输入文本，或语音对话。输入s保存文件\n\n")
    print("- 🎙️：输入「t」，开始语音对话")
    print("- 🎹：输入文本，开始对话")
    print("- 💾：输入「s」，结束对话，保存文件\n\n")

    user_message = input("You: ").lower()

    # 用户选择语音输入
    if user_message == "t":
        user_message = utils.transcribe_speech_to_text()  # 用户语音输入，讯飞语音转文本，返回文本
        utils.chat_with_mentor(user_message, thread_id, assistant_id)

    # 用户选择结束对话，获取大纲，程序终止
    elif user_message == "s":
        print("文书大纲已生成，请到文档区查看「对话记录」与「文书大纲」\n\n")

        utils.save_chatlog(chatlog_path, thread_id, user_name)
        genterate_report(chatlog_path, report_path)
        break

    # 用户选择文本输入
    else:
        utils.chat_with_mentor(user_message, thread_id, assistant_id)
