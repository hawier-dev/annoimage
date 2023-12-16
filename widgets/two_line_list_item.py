from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem


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

    def add_to_list(self, list_widget):
        item = QListWidgetItem(list_widget)
        item.setSizeHint(self.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, self)
