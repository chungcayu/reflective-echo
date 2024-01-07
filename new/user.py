import os
import sys


class User:
    def __init__(self, name):
        self.username = name
        self.avatar = None
        self.settings = None

    def __repr__(self):
        return f"User(name={self.name})"

    def __str__(self):
        return f"User {self.name}"

    def set_avatar(self, image_path=None):
        """设置用户头像。如果未提供image_path，则使用默认头像。"""
        if image_path and os.path.isfile(image_path):
            self.avatar = image_path
        else:
            self.avatar = "path/to/default/avatar.jpg"

    def get_avatar(self):
        """获取用户头像"""
        return self.avatar
