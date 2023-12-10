from PySide6.QtWidgets import QWidget, QHBoxLayout, QLabel
from PySide6.QtGui import QPixmap
from PySide6.QtCore import Qt

from constants import LOGO_SIZE, TITLE


class TitleWidget(QWidget):
    def __init__(self, parent=None, scaling=1.3):
        super(TitleWidget, self).__init__(parent)

        self.title_layout = QHBoxLayout()
        self.title_layout.setAlignment(Qt.AlignCenter)
        self.title_layout.setSpacing(20)

        self.app_logo = QLabel()
        self.app_logo.setPixmap(
            QPixmap("icons/logo.png").scaled(
                LOGO_SIZE * scaling,
                LOGO_SIZE * scaling,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
        )

        self.app_name = QLabel(TITLE)
        self.app_name.setStyleSheet(f"font-size: {int(15 * scaling)}px;")

        self.title_layout.addWidget(self.app_logo)
        self.title_layout.addWidget(self.app_name)

        self.setLayout(self.title_layout)
