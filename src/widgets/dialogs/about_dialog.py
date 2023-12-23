from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel, QDialog, QVBoxLayout, QPushButton

from src.utils.constants import (
    TITLE,
    VERSION,
    DESCRIPTION,
    GITHUB_REPO_URL,
    FULL_AUTHOR_NAME,
    ICON_PATH,
)


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("About")
        self.setContentsMargins(50, 50, 50, 50)

        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setPixmap(
            QPixmap(ICON_PATH).scaled(
                64, 64, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        app_name_label = QLabel(TITLE + " " + VERSION)
        app_name_label.setStyleSheet("font-size: 16px; font-weight: bold;")
        app_name_label.setAlignment(Qt.AlignCenter)

        description_label = QLabel(DESCRIPTION)
        description_label.setStyleSheet("font-size: 14px;")
        description_label.setAlignment(Qt.AlignCenter)

        author_label = QLabel(FULL_AUTHOR_NAME)
        author_label.setAlignment(Qt.AlignCenter)
        author_label.setStyleSheet("font-size: 12px; color: gray; ")

        github_label = QLabel(f'<a href="{GITHUB_REPO_URL}">GitHub Repository</a>')
        github_label.setAlignment(Qt.AlignCenter)
        github_label.setOpenExternalLinks(True)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.accept)

        layout.addWidget(logo_label)
        layout.addSpacing(10)
        layout.addWidget(app_name_label)
        layout.addWidget(description_label)
        layout.addWidget(author_label)
        layout.addWidget(github_label)
        layout.addSpacing(10)
        layout.addWidget(close_button)

        self.setLayout(layout)
