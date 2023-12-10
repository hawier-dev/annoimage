from PySide6.QtGui import QPalette, QColor
from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel


class TwoLineListItem(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()

        layout = QVBoxLayout()
        layout.setSpacing(1)
        self.setLayout(layout)

        title_label = QLabel(title)
        title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; background-color: transparent;"
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "color: gray; font-size: 11px; background-color: transparent;"
        )

        layout.addWidget(title_label)
        layout.addWidget(subtitle_label)
