import sys

from PySide6.QtCore import Qt
from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QApplication, QMainWindow, QWidget

from app_gui import AppGui


class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Labeling tool")
        self.setMinimumSize(600, 400)
        central_widget = QWidget()
        self.app_gui = AppGui(self)
        central_widget.setLayout(self.app_gui)

        self.setCentralWidget(central_widget)


def create_palette():
    palette = QPalette()
    palette.setColor(QPalette.Window, QColor(33, 33, 33))
    palette.setColor(QPalette.WindowText, Qt.white)
    palette.setColor(QPalette.Base, QColor(22, 22, 22))
    palette.setColor(QPalette.AlternateBase, QColor(53, 53, 53))
    palette.setColor(QPalette.ToolTipBase, Qt.black)
    palette.setColor(QPalette.ToolTipText, Qt.white)
    palette.setColor(QPalette.Text, Qt.white)
    palette.setColor(QPalette.Button, QColor(53, 53, 53))
    palette.setColor(QPalette.ButtonText, Qt.white)
    palette.setColor(QPalette.BrightText, Qt.red)
    palette.setColor(QPalette.Link, QColor(42, 130, 218))
    palette.setColor(QPalette.Highlight, QColor(42, 130, 218))
    palette.setColor(QPalette.HighlightedText, Qt.black)

    return palette


def main():
    app = QApplication()
    app.setPalette(create_palette())
    app.setStyleSheet(
        "*:focus {outline: none;} "
        "QWidget {border: 0px solid black;} "
        "QListWidget::item { height: 30px; background-color: #222222; margin: 1px;}"
        "QListWidget::item:selected { background-color: #444; color: #ffffff;}"
        "QListWidget::item:focus {outline: none;}"
    )
    window = MyApp()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
