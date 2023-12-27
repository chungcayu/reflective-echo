import sys
from PyQt6.QtWidgets import QApplication
from gui import ReflectiveEchoUI
from settings_manager import SettingsManager

def main():
    # 创建一个 QApplication 实例
    app = QApplication(sys.argv)

    # 创建 SettingsManager 实例
    settings_manager = SettingsManager()

    # 创建 ReflectiveEchoUI 实例，并传递 settings_manager
    main_window = ReflectiveEchoUI(settings_manager)

    # 显示主窗口
    main_window.show()

    # 开始事件循环
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
