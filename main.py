import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFontDatabase
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from app_gui import AppGui
from constants import *


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle(TITLE)
        self.setMinimumSize(600, 400)
        central_widget = QWidget()
        self.app_gui = AppGui(self)
        central_widget.setLayout(self.app_gui)

        self.setCentralWidget(central_widget)


def create_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(*hex_to_rgb(BACKGROUND_COLOR)))
    palette.setColor(QPalette.WindowText, QColor(*hex_to_rgb(FOREGROUND_COLOR)))
    palette.setColor(QPalette.Base, QColor(*hex_to_rgb(SURFACE_COLOR)))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(*hex_to_rgb(PRIMARY_COLOR)))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    return palette


def main():
    app = QApplication()
    QFontDatabase.addApplicationFont('fonts/Inter-Medium.ttf')
    app.setPalette(create_palette())
    app.setStyleSheet(
        "*:focus {outline: none;} "
        "* {font-family: Inter; font-size: 12px; color: white; border-radius: 5px;}"
        "QWidget {border: 0px solid black;} "
        "QListWidget::item { height: 30px; background-color: #444; margin: 1px;}"
        "QListWidget::item:selected { background-color: #666; color: #ffffff;}"
        "QListWidget::item:focus {outline: none;}"
        "QToolBar {border: none; margin: 0px; padding: 0px; spacing: 0px;}"
        "QToolButton {background-color: " + f"{BACKGROUND_COLOR}" + "; border: none; color: #ffffff; padding: 10px; margin-bottom: 5px;}"
        "QToolButton:hover {background-color:" + f"{HOVER_COLOR}" + ";}"
        "QToolButton:checked {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QToolButton:pressed {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QPushButton {border: 1px solid " + f"{SURFACE_COLOR}" + "; padding: 5px;}"
        "QPushButton:hover {background-color: " + f"{PRIMARY_COLOR}" + ";}"
    )
    window = MyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
