import sys
from PyQt6.QtWidgets import QApplication, QMainWindow

from default_ui import DefaultUI
from chat_ui import ChatUI


class UIManager:
    def __init__(self):
        self.app = QApplication(sys.argv)
        self.main_window = QMainWindow()
        self.main_window.setWindowTitle("ReflectiveEcho")
        self.main_window.setMinimumSize(600, 800)
        self.main_window.setStyleSheet("background-color: #FFFBF5;")

        self.default_ui = DefaultUI(self)
        self.chat_ui = ChatUI(self)
        self.setup_menu_bar()

        self.main_window.setCentralWidget(self.default_ui)
        self.main_window.show()

    def run(self):
        self.app.exec()

    def show_default_ui(self):
        self.default_ui = DefaultUI(self)
        self.main_window.setCentralWidget(self.default_ui)

    def show_chat_ui(self):
        self.chat_ui = ChatUI(self)
        self.main_window.setCentralWidget(self.chat_ui)

    def setup_menu_bar(self):
        menu_bar = self.main_window.menuBar()

        # File menu
        file_menu = menu_bar.addMenu("File")
        file_menu.addAction("Open Folder")

        # View menu
        view_menu = menu_bar.addMenu("Settings")
        view_menu.addAction("Settings")
        view_menu.addAction("Templates")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Documentation")
