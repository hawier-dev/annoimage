import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor, QFontDatabase, QIcon
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
    QFontDatabase.addApplicationFont("fonts/Inter-Medium.ttf")
    QFontDatabase.addApplicationFont("fonts/Inter-Bold.ttf")
    app.setPalette(create_palette())
    app.setStyleSheet(
        "*:focus {outline: none;} "
        "* {font-family: Inter; font-size: 12px; color: white; border-radius: 5px;}"
        "QWidget {border: 0px solid black;} "
        "QListWidget::item { height: 30px; background-color: #444; margin: 1px;}"
        "QListWidget::item:selected { background-color: #666; color: #ffffff;}"
        "QListWidget::item:focus {outline: none;}"
        "QToolBar {border: none; margin: 0px; padding: 0px; spacing: 0px;}"
        "QToolButton {background-color: "
        + f"{BACKGROUND_COLOR}"
        + "; border: none; color: #ffffff; padding: 10px; margin-bottom: 5px; margin-left:5px;}"
        "QToolButton:hover {background-color:" + f"{HOVER_COLOR}" + ";}"
        "QToolButton:checked {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QToolButton:pressed {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QPushButton {border: 1px solid " + f"{SURFACE_COLOR}" + "; padding: 5px;}"
        "QPushButton:hover {background-color: " + f"{PRIMARY_COLOR}" + ";}"
        "QScrollBar:vertical {border: none; background: "
        + f"{SURFACE_COLOR};"
        + " width: 18px; margin: 0px 0px 0px 0px;border-radius: 0px;}"
        "QScrollBar::handle:vertical {background: "
        + f"{BACKGROUND_COLOR2}"
        + "; min-height: 0px;}"
        "QScrollBar::add-line:vertical {background: "
        + f"{BACKGROUND_COLOR}"
        + "; height: 0px; subcontrol-position: bottom;}"
        "QScrollBar::sub-line:vertical {background: "
        + f"{BACKGROUND_COLOR}"
        + "; height: 0px; subcontrol-position: top;}"
        "QScrollBar::up-arrow:vertical, QScrollBar::down-arrow:vertical {background: none;}"
        "QScrollBar::add-page:vertical, QScrollBar::sub-page:vertical {background: none;}"
        "QScrollBar:horizontal {border: none; background: "
        + f"{SURFACE_COLOR};"
        + " height: 18px; margin: 0px 0px 0px 0px;border-radius: 0px;}"
        "QScrollBar::handle:horizontal {background: "
        + f"{BACKGROUND_COLOR2}"
        + "; min-width: 0px;}"
        "QScrollBar::add-line:horizontal {background: "
        + f"{BACKGROUND_COLOR}"
        + "; width: 0px; subcontrol-position: right;}"
        "QScrollBar::sub-line:horizontal {background: "
        + f"{BACKGROUND_COLOR}"
        + "; width: 0px; subcontrol-position: left;}"
        "QScrollBar::left-arrow:horizontal, QScrollBar::right-arrow:horizontal {background: none;}"
        "QScrollBar::add-page:horizontal, QScrollBar::sub-page:horizontal {background: none;}"
        "QComboBox {border: 1px solid " + f"{SURFACE_COLOR}" + "; padding: 5px;}"
        "QComboBox:hover {background-color: " + f"{HOVER_COLOR}" + ";}"
        "QComboBox QAbstractItemView {background-color: " + f"{BACKGROUND_COLOR}" + "; padding: 10px;}"
        "QComboBox QAbstractItemView::item {height: 30px;}"
        "QComboBox QAbstractItemView::item:selected {background-color: " + f"{PRIMARY_COLOR}" + "; color: #ffffff;}"
        "QComboBox::drop-down {border: none;}"
        "QComboBox::down-arrow {image: url(icons/arrow_down.png); width: 15px; height: 15px;}"
        "QTableWidget::item {background-color: " + f"{SURFACE_COLOR}" + ";}"
        "QTableWidget::item:selected {background-color: " + f"{PRIMARY_COLOR}" + "; color: #ffffff;}"
        "QTableWidget::item:focus {outline: none;}"
        "QHeaderView::section {background-color: " + f"{BACKGROUND_COLOR}" + "; color: #ffffff; border: none; padding: 5px;}"
        "QHeaderView::section:checked {background-color: " + f"{BACKGROUND_COLOR2}" + ";}"
        "QHeaderView::section:pressed {background-color: " + f"{BACKGROUND_COLOR2}" + ";}"
        "QHeaderView::section:checked:disabled {background-color: " + f"{BACKGROUND_COLOR2}" + ";}"
        "QTableCornerButton::section { background-color: " + f"{SURFACE_COLOR}" + ";}"
        "QMenu {background-color: " + f"{BACKGROUND_COLOR}" + ";}"
        "QMenu::item {background-color: " + f"{BACKGROUND_COLOR}" + "; color: #ffffff; padding: 5px;}"
        "QMenu::item:selected {background-color: " + f"{PRIMARY_COLOR}" + "; color: #ffffff;}"
        "QMenu::item:pressed {background-color: " + f"{PRIMARY_COLOR}" + "; color: #ffffff;}"
        "QMenu::item:disabled {background-color: " + f"{BACKGROUND_COLOR}" + "; color: #ffffff;}"
    )
    window = MyApp()
    icon = QIcon("icons/logo.png")
    window.setWindowIcon(icon)

    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
