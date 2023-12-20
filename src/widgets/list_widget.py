from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import QListWidget


class ListWidget(QListWidget):
    delete_pressed = Signal()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_pressed.emit()
        else:
            super().keyPressEvent(event)
