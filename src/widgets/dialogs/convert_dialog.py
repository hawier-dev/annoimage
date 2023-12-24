from PySide6.QtCore import Qt
from PySide6.QtGui import QFont
from PySide6.QtWidgets import (
    QDialog,
    QVBoxLayout,
    QHBoxLayout,
    QLabel,
    QComboBox,
    QRadioButton,
    QLineEdit,
    QPushButton,
    QFileDialog,
    QWidget,
    QSizePolicy,
)


class ExportDialog(QDialog):
    def __init__(self, anno_project):
        super().__init__()

        self.setWindowTitle("Export Project")
        self.setMinimumWidth(350)
        self.anno_project = anno_project

        self.layout = QVBoxLayout(self)

        self.title_label = QLabel("Export Project")
        self.title_label.setStyleSheet("font-weight: bold; font-size: 14px;")
        self.layout.addWidget(self.title_label)
        self.layout.addSpacing(10)

        # Dataset type selection
        self.dataset_type_label = QLabel("Select dataset type:")
        self.dataset_type_combo = QComboBox()
        self.dataset_type_combo.addItems(["COCO", "YOLO"])
        self.dataset_type_combo.currentIndexChanged.connect(self.toggle_yolo_options)
        self.layout.addWidget(self.dataset_type_label)
        self.layout.addWidget(self.dataset_type_combo)

        # Polygon options - hidden by default
        self.polygons_label = QLabel("What to do with polygons?")
        self.polygon_options = QWidget()
        self.polygon_layout = QHBoxLayout(self.polygon_options)
        self.ignore_polygons_radio = QRadioButton("Ignore polygons")
        self.convert_polygons_radio = QRadioButton("Convert to rectangles")
        self.ignore_polygons_radio.setChecked(True)
        self.polygon_layout.addWidget(self.ignore_polygons_radio)
        self.polygon_layout.addWidget(self.convert_polygons_radio)
        self.layout.addWidget(self.polygons_label)
        self.layout.addWidget(self.polygon_options)

        # Save empty files - hidden by default
        self.empty_files_label = QLabel("What to do with empty label files?")
        self.empty_files_options = QWidget()
        self.empty_files_layout = QHBoxLayout(self.empty_files_options)
        self.save_empty_files_radio = QRadioButton("Save")
        self.ignore_empty_radio = QRadioButton("Ignore")
        self.ignore_empty_radio.setChecked(True)
        self.empty_files_layout.addWidget(self.save_empty_files_radio)
        self.empty_files_layout.addWidget(self.ignore_empty_radio)
        self.layout.addWidget(self.empty_files_label)
        self.layout.addWidget(self.empty_files_options)

        self.toggle_yolo_options()

        # Save path
        self.save_path_label = QLabel("Save path:")
        self.save_path_layout = QHBoxLayout()
        self.save_path_line_edit = QLineEdit()
        self.save_path_line_edit.setReadOnly(True)
        self.save_path_line_edit.setPlaceholderText("Select a directory")
        self.save_path_line_edit.textChanged.connect(self.check_export_ready)
        self.browse_button = QPushButton("...")
        self.browse_button.clicked.connect(self.browse)
        self.browse_button.setFixedHeight(self.save_path_line_edit.sizeHint().height())
        self.save_path_layout.addWidget(self.save_path_line_edit)
        self.save_path_layout.addWidget(self.browse_button)
        self.layout.addWidget(self.save_path_label)
        self.layout.addLayout(self.save_path_layout)

        # Action buttons
        self.layout.addStretch()
        self.export_button = QPushButton("Export")
        self.export_button.clicked.connect(self.export)
        self.export_button.setEnabled(False)
        self.cancel_button = QPushButton("Cancel")
        self.cancel_button.clicked.connect(self.reject)
        self.layout.addWidget(self.export_button)
        self.layout.addWidget(self.cancel_button)

    def toggle_yolo_options(self):
        is_yolo = self.dataset_type_combo.currentText() == "YOLO"
        self.polygons_label.setVisible(is_yolo)
        self.polygon_options.setVisible(is_yolo)
        self.empty_files_label.setVisible(is_yolo)
        self.empty_files_options.setVisible(is_yolo)

    def browse(self):
        folder_path = QFileDialog.getExistingDirectory(self, "Select a directory")
        if folder_path:
            self.save_path_line_edit.setText(folder_path)

    def check_export_ready(self):
        # Enable the export button only if the line edit is not empty
        self.export_button.setEnabled(bool(self.save_path_line_edit.text()))

    def export(self):
        # Export data logic goes here
        dataset_type = self.dataset_type_combo.currentText()
        ignore_polygons = (
            self.ignore_polygons_radio.isChecked() if dataset_type == "YOLO" else None
        )
        save_empty_files = (
            self.save_empty_files_radio.isChecked() if dataset_type == "YOLO" else None
        )
        save_path = self.save_path_line_edit.text()

        self.anno_project.export_project(
            dataset_type, ignore_polygons, save_empty_files, save_path
        )
        self.accept()
