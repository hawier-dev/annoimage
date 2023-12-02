from PySide6.QtWidgets import QStyledItemDelegate


class ListWidgetDelegate(QStyledItemDelegate):
    def initStyleOption(self, option, index):
        super().initStyleOption(option, index)
        option.text = f"{index.row() + 1}. {option.text}"
