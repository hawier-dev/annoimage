from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout

from src.widgets.dialogs.centered_dialog import CenteredDialog


class ErrorDialog(CenteredDialog):
    def __init__(self, widget, window_title, title, text, url=""):
        super(ErrorDialog, self).__init__(widget)

        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("font-size: 13px;")
        if url:
            self.description_label = QLabel(f'More information here: <a href="{url}">{url}</a>')
            self.description_label.setStyleSheet("font-size: 13px; color: gray;")
            self.description_label.setOpenExternalLinks(True)
        else:
            self.description_label = QLabel()
            self.description_label.setVisible(False)

        self.hor_layout = QHBoxLayout()
        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        self.button_ok.setShortcut(Qt.Key_Return)

        self.hor_layout.addWidget(self.button_ok)
        self.hor_layout.setAlignment(Qt.AlignCenter)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.description_label)
        self.layout.addStretch()
        self.layout.addLayout(self.hor_layout)

        self.setLayout(self.layout)
        self.center_pos()
