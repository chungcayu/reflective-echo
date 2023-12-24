# security_helper.py
from cryptography.fernet import Fernet
import os

key_path = "./data/secret.key"


def generate_key():
    key = Fernet.generate_key()
    with open(key_path, "wb") as key_file:
        key_file.write(key)


def load_key():
    if not os.path.exists(key_path):
        generate_key()
    return open(key_path, "rb").read()


def encrypt_api_key(api_key, file_path):
    key = load_key()
    f = Fernet(key)
    encrypted_api_key = f.encrypt(api_key.encode())
    with open(file_path, "wb") as file:
        file.write(encrypted_api_key)


def decrypt_api_key(encrypted_file_path):
    key = load_key()
    f = Fernet(key)
    try:
        with open(encrypted_file_path, "rb") as file:
            encrypted_api_key = file.read()
        return f.decrypt(encrypted_api_key).decode()
    except FileNotFoundError:
        print(f"Encrypted API key file not found: {encrypted_file_path}")
        return ""
    except Exception as e:
        print(f"Error decrypting API key: {e}")
        return ""
