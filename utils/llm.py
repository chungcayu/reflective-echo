# llm.py
import os
import time
from dotenv import load_dotenv
from openai import OpenAI

from .settings import get_api_key


"""
调用 OpenAI API
"""
load_dotenv()

openai_api_key = get_api_key("openai_api_key")
client = OpenAI(api_key=openai_api_key)


def get_assistant_id():
    return os.getenv("OPENAI_ASSISTANT_ID")


# Create a thread
def create_thread():
    thread = client.beta.threads.create()
    return thread.id


# Creata a message
def create_message(prompt, thread_id):
    message = client.beta.threads.messages.create(
        thread_id=thread_id,
        role="user",
        content=prompt,
    )
    return message


# Run the assistant
def run_thread(thread_id, assistant_id):
    run = client.beta.threads.runs.create(
        thread_id=thread_id,
        assistant_id=assistant_id,
    )
    return run.id


# Check the status of the run
def check_run_status(thread_id, run_id):
    run_list = client.beta.threads.runs.retrieve(
        thread_id=thread_id,
        run_id=run_id,
    )
    return run_list.status


def retrieve_message_list(thread_id):
    messages = client.beta.threads.messages.list(
        thread_id=thread_id,
    )
    return messages.data


# Chat Completion
def generate_text_from_oai(system_prompt, user_message):
    response = client.chat.completions.create(
        model="gpt-3.5-turbo-1106",  # gpt-3.5-turbo-1106 | gpt-4-1106-preview
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_message},
        ],
        temperature=0.5,
    )
    return response.choices[0].message.content
