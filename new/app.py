import sys
import os
from PyQt6.QtWidgets import QApplication

from ui_manager import UIManager

basedir = os.path.dirname(__file__)

if __name__ == "__main__":
    manager = UIManager()
    manager.run()
