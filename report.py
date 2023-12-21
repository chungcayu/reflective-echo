import llm

system_prompt = """
    你是一个报告写作大师。你的导师要求你写一份周总结。
    template = {
    }
    """


def genterate_report(chatlog_path, report_path):
    with open(chatlog_path, "r") as file:
        user_message = file.read()

    response = llm.generate_text_from_oai(system_prompt, user_message)
    with open(report_path, "w") as file:
        file.write(response)
    print("您的周总结成功生成\n\n")
