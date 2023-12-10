from PySide6.QtCore import Qt, Signal
from PySide6.QtWidgets import (
    QWidget,
    QVBoxLayout,
    QHBoxLayout,
    QPushButton,
    QLabel,
    QListWidget,
    QComboBox,
    QLineEdit,
    QFileDialog,
    QAbstractItemView,
    QDialog,
)

from constants import DATASET_TYPES
from models.anno_project import AnnoProject
from models.label_image import LabelImage
from utils.list_widget_delegate import ListWidgetDelegate
from widgets.add_label_dialog import AddLabelDialog
from widgets.title_widget import TitleWidget


class NewProjectWidget(QWidget):
    project_created = Signal(AnnoProject)

    def __init__(self, parent=None):
        super().__init__()
        self.setContentsMargins(10, 10, 10, 10)
        self.parent = parent

        self.main_layout = QVBoxLayout()
        self.title_widget = TitleWidget(scaling=1.1)

        self.project_layout = QHBoxLayout()

        # Vertical layout for the project name
        self.project_name_layout = QVBoxLayout()
        self.project_name_label = QLabel("Project Name")
        self.project_name_edit = QLineEdit()
        self.project_name_edit.setText("new_project")
        self.project_name_edit.textChanged.connect(
            self.update_create_button
        )  # Track text changes

        self.project_name_layout.addWidget(self.project_name_label)
        self.project_name_layout.addWidget(self.project_name_edit)

        # Vertical layout for the data set type
        self.dataset_type_layout = QVBoxLayout()

        self.dataset_type_label = QLabel("Dataset Type")
        self.dataset_type_combo = QComboBox()
        self.dataset_type_combo.addItems(DATASET_TYPES)

        self.dataset_type_layout.addWidget(self.dataset_type_label)
        self.dataset_type_layout.addWidget(self.dataset_type_combo)

        self.project_layout.addLayout(self.project_name_layout)
        self.project_layout.addLayout(self.dataset_type_layout)

        # Images and classes layout
        self.lists_layout = QHBoxLayout()

        # Images List and Buttons
        self.images_layout = QVBoxLayout()
        self.images_list_label = QLabel("Images")
        self.images_list = QListWidget()
        self.images_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.images_buttons_layout = QHBoxLayout()
        self.images_add_button = QPushButton("Add")
        self.images_add_button.clicked.connect(self.add_images)
        self.images_delete_button = QPushButton("Delete")
        self.images_delete_button.clicked.connect(self.delete_images)
        self.images_buttons_layout.addWidget(self.images_add_button)
        self.images_buttons_layout.addWidget(self.images_delete_button)

        self.images_layout.addWidget(self.images_list_label)
        self.images_layout.addWidget(self.images_list)
        self.images_layout.addLayout(self.images_buttons_layout)

        # Class List and Buttons
        self.classes_layout = QVBoxLayout()
        self.classes_list_label = QLabel("Class Names")
        self.classes_list = QListWidget()
        self.classes_list.setSelectionMode(QAbstractItemView.ExtendedSelection)
        self.classes_list.setDragDropMode(QListWidget.InternalMove)
        delegate = ListWidgetDelegate()
        self.classes_list.setItemDelegate(delegate)
        self.classes_buttons_layout = QHBoxLayout()
        self.classes_add_button = QPushButton("Add")
        self.classes_add_button.pressed.connect(self.add_classes)
        self.classes_delete_button = QPushButton("Delete")
        self.classes_delete_button.pressed.connect(self.delete_classes)
        self.classes_buttons_layout.addWidget(self.classes_add_button)
        self.classes_buttons_layout.addWidget(self.classes_delete_button)

        self.classes_layout.addWidget(self.classes_list_label)
        self.classes_layout.addWidget(self.classes_list)
        self.classes_layout.addLayout(self.classes_buttons_layout)

        self.lists_layout.addLayout(self.images_layout)
        self.lists_layout.addSpacing(10)
        self.lists_layout.addLayout(self.classes_layout)

        # Bottom buttons layout
        self.button_layout = QHBoxLayout()
        self.back_button = QPushButton("Back")
        self.create_button = QPushButton("Create")
        self.create_button.pressed.connect(self.create_project)
        self.create_button.setEnabled(False)

        self.button_layout.addWidget(self.back_button)
        self.button_layout.addStretch()
        self.button_layout.addWidget(self.create_button)

        self.main_layout.addWidget(self.title_widget)
        self.main_layout.addLayout(self.project_layout)
        self.main_layout.addSpacing(5)
        self.main_layout.addLayout(self.lists_layout)
        self.main_layout.addSpacing(5)
        self.main_layout.addLayout(self.button_layout)

        self.setLayout(self.main_layout)
        for child in self.findChildren(QPushButton):
            child.setCursor(Qt.PointingHandCursor)

    def add_images(self):
        file_dialog = QFileDialog()
        image_files, _ = file_dialog.getOpenFileNames(
            self,
            caption="Select images",
            filter="Images (*.png *.jpg *.jpeg *.tif *.tiff)",
        )
        if image_files:
            for image in image_files:
                self.images_list.addItem(image)

        self.update_create_button()

    def delete_images(self):
        for item in self.images_list.selectedItems():
            self.images_list.takeItem(self.images_list.row(item))

        self.update_create_button()

    def add_classes(self):
        add_label_dialog = AddLabelDialog(self.parent)
        result = add_label_dialog.exec_()
        if result == QDialog.Accepted:
            class_name = add_label_dialog.label_name_input.text()
            if class_name:
                self.classes_list.addItem(class_name)

    def delete_classes(self):
        for item in self.classes_list.selectedItems():
            self.classes_list.takeItem(self.classes_list.row(item))

    def update_create_button(self):
        project_name = self.project_name_edit.text()
        number_of_images = self.images_list.count()

        # Check if project name is not empty and there is at least one image
        if project_name and number_of_images > 0:
            self.create_button.setEnabled(True)
        else:
            self.create_button.setEnabled(False)

    def create_project(self):
        project_name = self.project_name_edit.text()
        dataset_type = self.dataset_type_combo.currentText()
        images_paths = [
            self.images_list.item(i).text() for i in range(self.images_list.count())
        ]
        class_names = [
            self.classes_list.item(i).text() for i in range(self.classes_list.count())
        ]

        project = AnnoProject(
            main_window=self.parent,
            name=project_name,
            dataset_type=dataset_type,
            images=[
                LabelImage(image_id=i, labels=[], path=path)
                for i, path in enumerate(images_paths)
            ],
            class_names=class_names,
        )
        project.save_project()
        self.project_created.emit(project)
