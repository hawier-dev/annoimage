from PySide6.QtCore import Qt
from PySide6.QtGui import QIcon
from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton

from widgets.centered_dialog import CenteredDialog


class AddLabelDialog(CenteredDialog):
    def __init__(self, main_widget):
        super(AddLabelDialog, self).__init__(main_widget)
        self.setWindowTitle("Add Label")
        self.setGeometry(100, 100, 400, 100)

        self.layout = QVBoxLayout()

        self.label_name_input = QLineEdit()
        self.label_name_input.setPlaceholderText("Label Name")

        self.hor_layout = QHBoxLayout()
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.reject)
        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)
        self.button_ok.setShortcut(Qt.Key_Return)

        self.hor_layout.addWidget(self.button_cancel)
        self.hor_layout.addWidget(self.button_ok)

        self.layout.addWidget(self.label_name_input)
        self.layout.addStretch()
        self.layout.addLayout(self.hor_layout)

        self.setLayout(self.layout)
        self.center_pos()
