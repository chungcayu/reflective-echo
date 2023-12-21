# security.py
from cryptography.fernet import Fernet
import os


def generate_key():
    key = Fernet.generate_key()
    with open("secret.key", "wb") as key_file:
        key_file.write(key)


def load_key():
    if not os.path.exists("secret.key"):
        generate_key()
    return open("secret.key", "rb").read()


def encrypt_api_key(api_key, file_path):
    key = load_key()
    f = Fernet(key)
    encrypted_api_key = f.encrypt(api_key.encode())
    with open(file_path, "wb") as file:
        file.write(encrypted_api_key)


def decrypt_api_key():
    key = load_key()
    f = Fernet(key)
    with open("api_key.encrypted", "rb") as file:
        encrypted_api_key = file.read()
    return f.decrypt(encrypted_api_key).decode()
