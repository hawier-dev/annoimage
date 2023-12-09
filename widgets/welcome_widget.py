from PySide6.QtCore import Qt
from PySide6.QtWidgets import QWidget, QVBoxLayout, QHBoxLayout, QListWidget, QPushButton, QLabel
from PySide6.QtGui import QPixmap

from constants import *


class WelcomeWidget(QWidget):
    def __init__(self):
        super().__init__()
        self.setContentsMargins(100, 20, 100, 50)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)

        self.title_widget = QWidget()
        self.title_layout = QHBoxLayout()
        self.title_layout.setAlignment(Qt.AlignCenter)
        self.title_layout.setSpacing(20)

        self.app_logo = QLabel()
        self.app_logo.setPixmap(
            QPixmap("icons/logo.png").scaled(
                LOGO_SIZE * 1.3, LOGO_SIZE * 1.3, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.app_name = QLabel(TITLE)
        self.app_name.setStyleSheet("font-size: 20px;")

        self.title_layout.addWidget(self.app_logo)
        self.title_layout.addWidget(self.app_name)

        self.title_widget.setLayout(self.title_layout)
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
        self.open_button = QPushButton('Open Project')
        self.open_button.setCursor(Qt.PointingHandCursor)
        self.open_button.clicked.connect(self.open_project)
        self.buttons_layout.addWidget(self.open_button)

        self.load_button = QPushButton('Load Project')
        self.load_button.clicked.connect(self.load_project)
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

    def open_project(self):
        print('Open Project clicked')

    def load_project(self):
        print('Load Project clicked')