from PySide6.QtCore import Qt
from PySide6.QtGui import QPixmap
from PySide6.QtWidgets import QLabel


class LogoLabel(QLabel):
    def __init__(self, logo_path, size):
        super().__init__()
        self.setPixmap(
            QPixmap(logo_path).scaled(
                size, size, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )
        self.setAlignment(Qt.AlignCenter)
