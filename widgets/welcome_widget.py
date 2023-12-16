from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QListWidget,
    QPushButton,
    QLabel,
    QListWidgetItem,
)
from PySide6.QtGui import QPixmap

from constants import *
from widgets.title_widget import TitleWidget
from widgets.two_line_list_item import TwoLineListItem


class WelcomeWidget(QWidget):
    def __init__(self, last_projects):
        super().__init__()
        self.setContentsMargins(100, 20, 100, 20)
        self.main_layout = QVBoxLayout()
        self.main_layout.setAlignment(Qt.AlignCenter)
        # sort by date created
        last_projects = sorted(
            last_projects, key=lambda x: x["date_created"], reverse=True
        )

        self.title_widget = TitleWidget()
        self.main_layout.addWidget(self.title_widget)

        self.buttons_widget = QWidget()
        self.buttons_widget.setContentsMargins(0, 0, 0, 0)
        self.buttons_widget.setStyleSheet(
            "QPushButton {"
            f"background-color: {BUTTON_BACKGROUND};"
            "}"
            "QPushButton:hover {"
            f"background-color: {BUTTON_HOVER};"
            "}"
        )
        self.buttons_layout = QVBoxLayout()
        self.buttons_layout.setContentsMargins(0, 0, 0, 0)
        self.new_button = QPushButton("New Project")
        self.new_button.setCursor(Qt.PointingHandCursor)
        self.buttons_layout.addWidget(self.new_button)

        self.load_button = QPushButton("Load Project")
        self.load_button.setCursor(Qt.PointingHandCursor)
        self.buttons_layout.addWidget(self.load_button)

        self.buttons_widget.setLayout(self.buttons_layout)

        self.main_layout.addWidget(self.buttons_widget)

        self.project_list_label = QLabel("Last Projects")
        self.project_list = QListWidget()
        self.project_list.setStyleSheet(
            f"background-color: {BACKGROUND_COLOR};"
            "QListWidget::item {"
            f"background-color: {SURFACE_COLOR};"
            "}"
        )
        for project in last_projects:
            item_widget = TwoLineListItem(project["name"], project["path"])
            item_widget.add_to_list(self.project_list)

        if not last_projects:
            self.project_list_label.hide()
            self.project_list.hide()
        else:
            self.main_layout.addSpacing(20)

        self.main_layout.addWidget(self.project_list_label)
        self.main_layout.addWidget(self.project_list)

        self.setLayout(self.main_layout)
