from PySide6.QtWidgets import QWidget, QVBoxLayout, QLabel, QListWidgetItem

from src.utils.constants import SELECTED_COLOR


class TwoLineListItem(QWidget):
    def __init__(self, title, subtitle):
        super().__init__()

        self.title = title
        self.subtitle = subtitle
        layout = QVBoxLayout()
        layout.setSpacing(1)
        self.setLayout(layout)

        self.title_label = QLabel(title)
        self.title_label.setStyleSheet(
            "font-weight: bold; font-size: 12px; background-color: transparent;"
        )

        subtitle_label = QLabel(subtitle)
        subtitle_label.setStyleSheet(
            "color: gray; font-size: 11px; background-color: transparent;"
        )

        layout.addWidget(self.title_label)
        layout.addWidget(subtitle_label)

    def add_to_list(self, list_widget):
        item = QListWidgetItem(list_widget)
        item.setSizeHint(self.sizeHint())
        list_widget.addItem(item)
        list_widget.setItemWidget(item, self)

    def set_selected(self, selected):
        if selected:
            self.title_label.setStyleSheet(
                f"color: {SELECTED_COLOR};"
                f"font-weight: bold; font-size: 12px; background-color: transparent;"
            )
        else:
            self.title_label.setStyleSheet(
                f"color: white;"
                "font-weight: bold; font-size: 12px; background-color: transparent;"
            )
