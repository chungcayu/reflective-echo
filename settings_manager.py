import os
import json
from cryptography.fernet import Fernet, InvalidToken


class APIKeyManager:
    def __init__(self, key_path="./data/secret.key"):
        self.key_path = key_path
        self.key = self.load_key()

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
    def __init__(self, config_path="settings.json", key_manager=None):
        self.config_path = config_path
        self.key_manager = key_manager or APIKeyManager()
        self.settings = self.load_settings()

    def load_settings(self):
        try:
            with open(self.config_path, "r") as config_file:
                encrypted_settings = json.load(config_file)
                # Decrypt settings after loading
                return {
                    key: self.key_manager.decrypt_api_key(value)
                    for key, value in encrypted_settings.items()
                }
        except FileNotFoundError:
            print(f"Settings file not found: {self.config_path}")
            return {}

    def save_settings(self, new_settings):
        # Encrypt settings before saving
        encrypted_settings = {
            key: self.key_manager.encrypt_api_key(value)
            for key, value in new_settings.items()
        }
        with open(self.config_path, "w") as config_file:
            json.dump(encrypted_settings, config_file, indent=4)

    def get_setting(self, key):
        return self.settings.get(key)

    def update_setting(self, key, value):
        self.settings[key] = value
        self.save_settings(self.settings)


# Example usage:
if __name__ == "__main__":
    settings_manager = SettingsManager()
    settings_manager.update_setting("some_api_key", "some_api_key_value")
    print(settings_manager.get_setting("some_api_key"))
