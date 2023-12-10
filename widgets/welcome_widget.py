from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
)
from PySide6.QtGui import QPixmap

from constants import *
from widgets.title_widget import TitleWidget


class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(100, 20, 100, 50)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.title_widget = TitleWidget()
        self.main_layout.addWidget(self.title_widget)

        self.buttons_widget = QWidget()
        self.buttons_widget.setStyleSheet(
            "QPushButton {"
            f"background-color: {BUTTON_BACKGROUND};"
            "}"
            "QPushButton:hover {"
            f"background-color: {BUTTON_HOVER};"
            "}"
        )
        self.buttons_layout = QVBoxLayout()
        self.new_button = QPushButton("New Project")
        self.new_button.setCursor(Qt.PointingHandCursor)
        self.buttons_layout.addWidget(self.new_button)

        self.load_button = QPushButton("Load Project")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.buttons_layout.addWidget(self.load_button)

        self.buttons_widget.setLayout(self.buttons_layout)

        self.main_layout.addWidget(self.buttons_widget)

        self.project_list = QListWidget()
        self.project_list.setStyleSheet(
            f"background-color: {BACKGROUND_COLOR};"
            "QListWidget::item {"
            f"background-color: {SURFACE_COLOR};"
            "}"
        )
        self.main_layout.addWidget(self.project_list)

        self.setLayout(self.main_layout)
