from PySide6.QtCore import Qt
from PySide6.QtWidgets import QLabel, QVBoxLayout, QPushButton, QHBoxLayout

from src.widgets.dialogs.centered_dialog import CenteredDialog


class YesOrNoDialog(CenteredDialog):
    def __init__(self, widget, window_title, title, text, description="", cancel=False):
        super(YesOrNoDialog, self).__init__(widget)

        self.setWindowTitle(window_title)
        self.setGeometry(100, 100, 400, 100)

        self.canceled = False

        self.layout = QVBoxLayout()
        self.title_label = QLabel(title)
        self.title_label.setStyleSheet("font-size: 15px; font-weight: bold;")
        self.text_label = QLabel(text)
        self.text_label.setStyleSheet("font-size: 13px;")
        self.description_label = QLabel(description)
        self.description_label.setStyleSheet("font-size: 13px; color: gray;")

        self.hor_layout = QHBoxLayout()
        self.button_yes = QPushButton("Yes")
        self.button_yes.clicked.connect(self.accept)
        self.button_yes.setShortcut(Qt.Key_Return)
        self.button_no = QPushButton("No")
        self.button_no.clicked.connect(self.reject)
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.on_cancel_clicked)

        self.hor_layout.addWidget(self.button_yes)
        self.hor_layout.addWidget(self.button_no)
        if cancel:
            self.hor_layout.addWidget(self.button_cancel)

        self.layout.addWidget(self.title_label)
        self.layout.addWidget(self.text_label)
        self.layout.addWidget(self.description_label)
        self.layout.addStretch()
        self.layout.addLayout(self.hor_layout)

        self.setLayout(self.layout)
        self.center_pos()

    def on_cancel_clicked(self):
        self.canceled = True
        self.reject()
