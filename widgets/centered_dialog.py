from PySide6.QtWidgets import QDialog


class CenteredDialog(QDialog):
    def __init__(self, main_widget):
        super().__init__()
        self.main_widget = main_widget

    def center_pos(self):
        qr = self.main_widget.rect().center()
        cp = self.main_widget.mapToGlobal(qr)
        self.move(cp.x() - self.width() / 2, cp.y() - self.height() / 2)
