from PySide6.QtGui import QIcon
from PySide6.QtWidgets import (
    QHBoxLayout,
    QListWidget,
    QVBoxLayout,
    QLineEdit,
    QPushButton,
    QDialog,
)
from PySide6.QtCore import Qt

from utils.delegate import ListWidhetDelegate


class LabelsManageDialog(QDialog):
    def __init__(self, current_labels):
        super().__init__()

        self.setWindowTitle("Manage labels")
        self.setGeometry(100, 100, 400, 300)
        self.setWindowIcon(QIcon("icons/logo.png"))

        layout = QVBoxLayout()

        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(QListWidget.ExtendedSelection)
        self.list_widget.setDragDropMode(QListWidget.InternalMove)
        delegate = ListWidhetDelegate()
        self.list_widget.setItemDelegate(delegate)
        self.list_widget.addItems(current_labels)
        layout.addWidget(self.list_widget)

        input_layout = QHBoxLayout()
        self.line_edit = QLineEdit()
        self.line_edit.setPlaceholderText("New label name")
        self.line_edit.returnPressed.connect(self.add_item)
        self.line_edit.setFixedHeight(30)
        input_layout.addWidget(self.line_edit)

        add_button = QPushButton("+")
        add_button.setFixedSize(30, 30)
        add_button.clicked.connect(self.add_item)
        input_layout.addWidget(add_button)

        delete_button = QPushButton("-")
        delete_button.setFixedSize(30, 30)
        delete_button.clicked.connect(self.delete_selected_items)
        input_layout.addWidget(delete_button)

        ok_button = QPushButton("OK")
        ok_button.clicked.connect(self.accept)

        layout.addLayout(input_layout)
        layout.addWidget(ok_button)

        self.setLayout(layout)

    def add_item(self):
        text = self.line_edit.text()
        if text and text not in [
            self.list_widget.item(i).text() for i in range(self.list_widget.count())
        ]:
            self.list_widget.addItem(text)
            self.line_edit.clear()

    def delete_selected_items(self):
        selected_items = self.list_widget.selectedItems()
        for item in selected_items:
            self.list_widget.takeItem(self.list_widget.row(item))

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_items()
