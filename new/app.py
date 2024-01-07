import sys
import os
from PyQt6.QtWidgets import QApplication

from main_gui import ReflectiveEchoUI

basedir = os.path.dirname(__file__)


def main():
    app = QApplication(sys.argv)
    window = ReflectiveEchoUI()
    window.show()
    app.exec()


if __name__ == "__main__":
    main()