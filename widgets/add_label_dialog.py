from PySide6.QtWidgets import QDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QPushButton


class AddLabelDialog(QDialog):
    def __init__(self):
        super(AddLabelDialog, self).__init__()
        self.setWindowTitle("Add Label")

        self.layout = QVBoxLayout()

        self.label_name_input = QLineEdit()
        self.label_name_input.setPlaceholderText("Label Name")
        self.label_name_input.setStyleSheet(
            "font-size: 13px; padding: 5px; border: 1px solid gray; border-radius: 5px;"
        )

        self.hor_layout = QHBoxLayout()
        self.button_cancel = QPushButton("Cancel")
        self.button_cancel.clicked.connect(self.reject)
        self.button_ok = QPushButton("OK")
        self.button_ok.clicked.connect(self.accept)

        self.hor_layout.addWidget(self.button_cancel)
        self.hor_layout.addWidget(self.button_ok)

        self.layout.addWidget(self.label_name_input)
        self.layout.addLayout(self.hor_layout)

        self.setLayout(self.layout)
