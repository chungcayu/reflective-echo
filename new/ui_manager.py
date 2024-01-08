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
        # self.setStyleSheet("background-color: #FFFBF5;")

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
        file_menu.addAction("New")
        file_menu.addAction("Open")
        file_menu.addAction("Save")
        file_menu.addAction("Save As")
        file_menu.addSeparator()
        file_menu.addAction("Exit")

        # Edit menu
        edit_menu = menu_bar.addMenu("Edit")
        edit_menu.addAction("Undo")
        edit_menu.addAction("Redo")
        edit_menu.addSeparator()
        edit_menu.addAction("Cut")
        edit_menu.addAction("Copy")
        edit_menu.addAction("Paste")
        edit_menu.addSeparator()
        edit_menu.addAction("Find")
        edit_menu.addAction("Replace")
        edit_menu.addAction("Select All")

        # View menu
        view_menu = menu_bar.addMenu("View")
        view_menu.addAction("Zoom In")
        view_menu.addAction("Zoom Out")
        view_menu.addAction("Reset Zoom")
        view_menu.addSeparator()
        view_menu.addAction("Toggle Full Screen")

        # Help menu
        help_menu = menu_bar.addMenu("Help")
        help_menu.addAction("About")
        help_menu.addAction("Documentation")
        help_menu.addAction("Report Issue")
