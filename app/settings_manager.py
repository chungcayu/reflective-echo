import os
import json
import platform
import sys

from cryptography.fernet import Fernet, InvalidToken

import logging

logger = logging.getLogger(__name__)


def get_user_data_dir():
    """
    获取应用程序的用户数据目录。这通常是 ~/Library/Application Support/ReflectiveEcho。
    """
    home = os.path.expanduser("~")
    return os.path.join(home, "Library", "Application Support", "ReflectiveEcho")


def ensure_app_data_dir_exists():
    """
    确保应用程序的数据目录存在。如果不存在，则创建它。
    """
    app_data_dir = get_user_data_dir()
    if not os.path.exists(app_data_dir):
        os.makedirs(app_data_dir)
    return app_data_dir


class APIKeyManager:
    def __init__(self, key_path=None):
        self.key_path = key_path or self.get_default_key_path()
        self.key = self.load_key()

    def get_default_key_path(self):
        key_path = ensure_app_data_dir_exists()
        return os.path.join(key_path, "secret.key")

    def generate_key(self):
        key = Fernet.generate_key()
        with open(self.key_path, "wb") as key_file:
            key_file.write(key)

    def load_key(self):
        if not os.path.exists(self.key_path):
            self.generate_key()
        with open(self.key_path, "rb") as key_file:
            return key_file.read()

    def encrypt_api_key(self, api_key):
        f = Fernet(self.key)
        return f.encrypt(api_key.encode()).decode()

    def decrypt_api_key(self, encrypted_api_key):
        f = Fernet(self.key)
        try:
            return f.decrypt(encrypted_api_key.encode()).decode()
        except FileNotFoundError:
            print(f"Encrypted API key file not found: {encrypted_api_key}")
        except InvalidToken:
            print(f"Invalid key - decryption failed for API key.")
        except Exception as e:
            print(f"Error decrypting API key: {e}")
        return ""


class SettingsManager:
    def __init__(self, config_path=None, key_manager=None):
        self.key_manager = key_manager or APIKeyManager()
        self.config_path = config_path or self.get_default_config_path()
        self.settings = self.load_settings()

    def get_default_config_path(self):
        config_path = ensure_app_data_dir_exists()
        return os.path.join(config_path, "settings.json")

    def load_settings(self):
        print("正在加载设置...")
        if not os.path.exists(self.config_path):
            # 如果配置文件不存在，创建一个默认配置
            self.save_settings(self.default_settings)
            return self.default_settings
        with open(self.config_path, "r") as config_file:
            encrypted_settings = json.load(config_file)
            settings = {
                key: self.key_manager.decrypt_api_key(value)
                for key, value in encrypted_settings.items()
            }
            return settings

    def save_settings(self, new_settings):
        print("正在保存设置...")
        # Encrypt settings before saving
        encrypted_settings = {
            key: self.key_manager.encrypt_api_key(value)
            for key, value in new_settings.items()
        }
        with open(self.config_path, "w") as config_file:
            json.dump(encrypted_settings, config_file, indent=4)
        self.reload_settings()  # 保存后重新加载设置，这个方法很重要

    def reload_settings(self):
        # 从文件重新加载设置
        self.settings = self.load_settings()

    def get_setting(self, key):
        return self.settings.get(key)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)

    @property
    def default_settings(self):
        # 默认设置可以根据您的需要进行调整
        return {
            "user_name": "",
            "save_location": "",
            "openai_api_key": "",
            "xunfei_app_id": "",
            "xunfei_api_key": "",
            # "minimax_group_id": "",
            # "minimax_api_key": "",
            "volcano_app_id": "",
            "volcano_access_token": "",
        }

    def isSettingsFilled(self):
        # 定义必要的设置项
        required_settings = [
            "openai_api_key",
            "xunfei_app_id",
            "xunfei_api_key",
            # "minimax_group_id",
            # "minimax_api_key",
            "volcano_app_id",
            "volcano_access_token",
        ]

        # 确保所有必要的设置都已被填写
        for key in required_settings:
            if not self.get_setting(key):
                return False
        return True
