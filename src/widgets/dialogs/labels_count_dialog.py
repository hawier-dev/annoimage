from PySide6.QtWidgets import (
    QVBoxLayout,
    QTableWidget,
    QTableWidgetItem,
    QHeaderView,
    QScrollArea,
)

from src.widgets.dialogs.centered_dialog import CenteredDialog


class LabelsCountDialog(CenteredDialog):
    def __init__(self, widget, label_names, label_paths: list, label_type="YOLO"):
        super().__init__(widget)

        self.setWindowTitle("Labels count")
        self.setGeometry(100, 100, 400, 300)

        # Table with count
        self.table = QTableWidget()
        self.table.setColumnCount(2)
        self.table.setHorizontalHeaderLabels(["Label", "Count"])
        self.table.setRowCount(len(label_names))
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Stretch)

        for i, label_name in enumerate(label_names):
            self.table.setItem(i, 0, QTableWidgetItem(label_name))

        if label_type == "YOLO":
            counts = [0 for _ in range(len(label_names))]
            for i, label_path in enumerate(label_paths):
                with open(label_path, "r") as label_file:
                    for line in label_file.readlines():
                        label_id = int(line.split(" ")[0])
                        counts[label_id] += 1

        elif label_type == "COCO":
            pass

        for i, count in enumerate(counts):
            self.table.setItem(i, 1, QTableWidgetItem(str(count)))

        scroll_area = QScrollArea()
        scroll_area.setWidget(self.table)
        scroll_area.setWidgetResizable(True)

        layout = QVBoxLayout()
        layout.addWidget(scroll_area)

        self.setLayout(layout)
        self.center_pos()
