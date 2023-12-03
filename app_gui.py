import os

from PySide6.QtCore import QSize, Qt, QEvent, QModelIndex
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QToolBar,
    QListWidget,
    QLabel,
    QPushButton,
    QLineEdit,
    QComboBox,
    QMessageBox,
    QMenu,
    QWidgetAction,
    QDialog,
)

from constants import *
from widgets.image_view import ImageView
from widgets.labels_count_dialog import LabelsCountDialog
from widgets.labels_manage_dialog import LabelsManageDialog
from widgets.list_widget import ListWidget
from widgets.yes_or_no_dialog import YesOrNoDialog


class AppGui(QVBoxLayout):
    def __init__(self, parent=None):
        super(AppGui, self).__init__(parent)
        self.main_window = parent
        self.images = []
        self.labels_names = []
        self.saved = True

        self.setContentsMargins(0, 0, 0, 0)

        # Top bar with app name and qcombobox with annotation types
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("padding: 5px;")
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.app_logo = QLabel()
        self.app_logo.setPixmap(
            QPixmap("icons/logo.png").scaled(
                LOGO_SIZE, LOGO_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.app_name = QLabel(TITLE)
        self.app_name.setStyleSheet("font-size: 15px;")

        # Dataset type selector
        self.dataset_type_selector = QComboBox()
        self.dataset_type_selector.addItems(["YOLO", "COCO"])
        self.dataset_type_selector.setFixedWidth(100)
        self.dataset_type_selector.currentTextChanged.connect(self.set_dataset_type)

        # Open directory button
        self.open_directory_button = QPushButton("Open directory")
        self.open_directory_button.clicked.connect(self.open_directory)

        self.open_file_button = QPushButton("Open files")
        self.open_file_button.clicked.connect(self.open_file)

        self.label_name_selector = QComboBox()
        self.label_name_selector.setFixedWidth(100)
        self.label_name_selector.currentTextChanged.connect(self.set_label_name)

        self.top_bar_layout.addSpacing(8)
        self.top_bar_layout.addWidget(self.app_logo)
        self.top_bar_layout.addWidget(self.app_name)
        self.top_bar_layout.addSpacing(8)
        self.top_bar_layout.addWidget(self.dataset_type_selector)

        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.label_name_selector)
        self.top_bar_layout.addWidget(self.open_directory_button)
        self.top_bar_layout.addWidget(self.open_file_button)
        self.top_bar_layout.addSpacing(8)

        self.top_bar.setLayout(self.top_bar_layout)

        # Main widget with image viewer and toolbar
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # Left toolbars
        self.left_toolbar = QToolBar("Tools")
        self.left_toolbar.setIconSize(QSize(TOOLBAR_ICON_SIZE, TOOLBAR_ICON_SIZE))
        self.left_toolbar.setMovable(False)
        self.left_toolbar.setOrientation(Qt.Vertical)

        self.select_button = QAction(QIcon("icons/select.png"), "Select (S)", self)
        self.select_button.triggered.connect(self.set_select_mode)
        self.select_button.setCheckable(True)
        self.select_button.setChecked(True)
        self.select_button.setShortcut("S")

        # Rectangular selection button
        self.rectangle_button = QAction(
            QIcon("icons/rect_selection.png"), "Rectangle (R)", self
        )
        self.rectangle_button.triggered.connect(self.set_rect_selection)
        self.rectangle_button.setCheckable(True)
        self.rectangle_button.setShortcut("R")

        # Polygonal selection button
        self.polygon_button = QAction(
            QIcon("icons/polygon_selection.png"), "Polygon (P) (ONLY IN COCO)", self
        )
        self.polygon_button.triggered.connect(self.set_polygon_selection)
        self.polygon_button.setCheckable(True)
        self.polygon_button.setShortcut("P")
        self.polygon_button.setEnabled(False)
        self.polygon_button.setVisible(False)

        self.previous_button = QAction(
            QIcon("icons/previous.png"), "Previous (Arrow Left)", self
        )
        self.previous_button.triggered.connect(self.previous_image)
        self.previous_button.setShortcut("Left")

        self.next_button = QAction(QIcon("icons/next.png"), "Next (Arrow Right)", self)
        self.next_button.triggered.connect(self.next_image)
        self.next_button.setShortcut("Right")

        self.save_button = QAction(QIcon("icons/save.png"), "Save (CTRL + S)", self)
        self.save_button.triggered.connect(self.save_labels)
        self.save_button.setShortcut("CTRL+S")

        self.left_toolbar.addAction(self.select_button)
        self.left_toolbar.addAction(self.rectangle_button)
        self.left_toolbar.addAction(self.polygon_button)
        self.left_toolbar.addAction(self.previous_button)
        self.left_toolbar.addAction(self.next_button)
        self.left_toolbar.addAction(self.save_button)

        # Center widget with image viewer
        self.center_layout = QVBoxLayout()

        self.image_view = ImageView(parent=self)
        self.image_view.label_added.connect(self.update_labels_list)
        self.image_view.updated_labels.connect(self.update_labels_list)
        self.image_view.drawing_label.connect(self.update_box_size_label)
        self.image_view.on_image_loaded.connect(self.set_current_image)
        self.image_view.scene().selectionChanged.connect(self.update_selection)

        self.center_layout.addWidget(self.image_view)

        self.right_panel_layout = QVBoxLayout()

        self.labels_label = QLabel("Labels")
        self.labels_list = ListWidget()
        self.labels_list.setMaximumWidth(RIGHT_MAXW)
        self.labels_list.setSelectionMode(QListWidget.SingleSelection)
        self.labels_list.itemSelectionChanged.connect(self.select_labels_from_list)
        self.labels_list.installEventFilter(self)
        self.labels_list.delete_pressed.connect(self.delete_selected_labels)

        self.manage_labels_button = QPushButton("Manage labels")
        self.manage_labels_button.setToolTip("Add or delete label names")
        self.manage_labels_button.clicked.connect(self.manage_labels)

        self.images_label = QLabel("Images")
        self.images_list = ListWidget()
        self.images_list.setMaximumWidth(RIGHT_MAXW)
        self.images_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.images_list.doubleClicked.connect(self.load_image)
        self.images_list.installEventFilter(self)
        self.images_list.delete_pressed.connect(self.delete_selected_photos)

        self.count_labels_button = QPushButton("Count all labels")
        self.count_labels_button.clicked.connect(self.count_all_labels)

        self.right_panel_layout.addWidget(self.labels_label)
        self.right_panel_layout.addWidget(self.labels_list)
        self.right_panel_layout.addWidget(self.manage_labels_button)
        self.right_panel_layout.addSpacing(10)
        self.right_panel_layout.addWidget(self.images_label)
        self.right_panel_layout.addWidget(self.images_list)
        self.right_panel_layout.addWidget(self.count_labels_button)

        self.main_layout.addWidget(self.left_toolbar)
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.right_panel_layout)

        # Bottom bar with output_path picker
        self.bottom_bar = QWidget()
        self.bottom_bar.setStyleSheet("padding: 5px;")
        self.bottom_bar_layout = QHBoxLayout()
        self.bottom_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.output_path_line_edit = QLineEdit()
        self.output_path_line_edit.setPlaceholderText("Output path")
        self.output_path_line_edit.setFixedHeight(30)
        self.output_path_line_edit.setReadOnly(True)

        self.output_path_button = QPushButton("...")
        self.output_path_button.setFixedSize(30, 30)
        self.output_path_button.clicked.connect(self.select_output_path)

        self.bottom_bar_layout.addSpacing(8)
        self.bottom_bar_layout.addWidget(self.output_path_line_edit)
        self.bottom_bar_layout.addWidget(self.output_path_button)
        self.bottom_bar_layout.addSpacing(8)

        self.bottom_bar.setLayout(self.bottom_bar_layout)

        self.status_bar = QWidget()
        self.status_bar.setStyleSheet("padding: 5px;")
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar_layout = QHBoxLayout()
        self.status_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.version = QLabel(f"{TITLE} {VERSION}")
        self.status_label = QLabel("Saved")
        self.set_saved(True)
        self.box_size_label = QLabel("")

        self.status_bar_layout.addWidget(self.version)
        self.status_bar_layout.addStretch()
        self.status_bar_layout.addWidget(self.box_size_label)
        self.status_bar_layout.addWidget(self.status_label)

        self.status_bar.setLayout(self.status_bar_layout)

        self.addSpacing(5)
        self.addWidget(self.top_bar)
        self.addLayout(self.main_layout)
        self.addWidget(self.bottom_bar)
        self.addWidget(self.status_bar)
        self.addSpacing(5)

        # self.main_window.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        # self.open_directory()

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.labels_list:
            item = source.itemAt(event.pos())
            menu = QMenu()

            if item is not None:
                title = QWidgetAction(menu)
                title.setDisabled(True)
                title_label = QLabel(item.text())
                title_label.setStyleSheet(
                    "font-size: 13px; padding: 5px;"
                    f"border-bottom: 1px solid {BACKGROUND_COLOR2};"
                )
                title.setDefaultWidget(title_label)
                menu.addAction(title)
                menu.addAction("Zoom to")

                selected_menu = menu.exec_(event.globalPos())
                if selected_menu is None:
                    return True
                elif selected_menu.text() == "Zoom to":
                    self.image_view.zoom_to_rect(item.text())

            return True
        elif event.type() == QEvent.ContextMenu and source is self.images_list:
            item = source.itemAt(event.pos())
            menu = QMenu()

            if item is not None:
                title = QWidgetAction(menu)
                title.setDisabled(True)
                title_label = QLabel(item.text())
                title_label.setStyleSheet(
                    "font-size: 13px; padding: 5px;"
                    f"border-bottom: 1px solid {BACKGROUND_COLOR2};"
                )
                title.setDefaultWidget(title_label)
                menu.addAction(title)
                menu.addAction("Load image")
                menu.addAction("Count labels")
                selected_menu = menu.exec_(event.globalPos())
                if selected_menu is None:
                    return True
                elif selected_menu.text() == "Load image":
                    self.load_image(self.images[self.images_list.row(item)])
                elif selected_menu.text() == "Count labels":
                    self.count_labels(self.images[self.images_list.row(item)])

            return True
        return super(QVBoxLayout, self).eventFilter(source, event)

    def load_image(self, image):
        if not self.saved:
            yes_no_dialog = YesOrNoDialog(
                self.main_window,
                "Save",
                "You have unsaved changes.",
                "Do you want to save them?",
                cancel=True,
            )
            result = yes_no_dialog.exec_()
            if result == YesOrNoDialog.Accepted:
                self.save_labels()
            elif result == YesOrNoDialog.Rejected and not yes_no_dialog.canceled:
                self.set_saved(True)
            else:
                return

        if type(image) is QModelIndex:
            self.image_view.load_image(self.images[image.row()])
        elif type(image) is str:
            self.image_view.load_image(image)

    def set_current_image(self, path):
        self.images_list.setCurrentRow(self.images.index(path))

    def update_box_size_label(self, box_size: tuple, drawing: bool):
        if not drawing:
            self.box_size_label.setText("")
        else:
            self.box_size_label.setText(f"{box_size[0], box_size[1]}")

    def set_dataset_type(self, dataset_type):
        self.image_view.dataset_type = dataset_type
        if dataset_type == "YOLO":
            self.polygon_button.setEnabled(False)
            self.polygon_button.setVisible(False)
        elif dataset_type == "COCO":
            self.polygon_button.setEnabled(True)
            self.polygon_button.setVisible(True)

    def set_label_name(self, label_name):
        self.image_view.label_name = label_name
        try:
            index = 0
            for i, name in enumerate(self.labels_names):
                if name == label_name:
                    index = i
                    break
            self.image_view.label_id = index
        except ValueError:
            self.image_view.label_id = None

    def manage_labels(self):
        labels_manage_dialog = LabelsManageDialog(self.main_window, self.labels_names)
        labels_manage_dialog.exec_()
        self.labels_names = [
            labels_manage_dialog.list_widget.item(i).text()
            for i in range(labels_manage_dialog.list_widget.count())
        ]

        self.update_labels_names()
        self.image_view.update_label_names()
        self.update_labels_list()

    def update_labels_names(self):
        current_items = [
            self.label_name_selector.itemText(i)
            for i in range(self.label_name_selector.count())
        ]
        self.label_name_selector.clear()
        self.label_name_selector.addItems(self.labels_names)

        self.image_view.labels_names = self.labels_names

    def open_directory(self):
        file_dialog = QFileDialog()

        directory = file_dialog.getExistingDirectory(
            None, "Select directory with images", ""
        )

        if directory:
            self.images = [
                os.path.join(directory, file)
                for file in os.listdir(directory)
                if file.endswith(".jpg")
            ]
            self.images_list.clear()
            self.images_list.addItems(
                [os.path.basename(image) for image in self.images]
            )

            if self.output_path_line_edit.text() == "":
                self.select_output_path(directory)
            else:
                yes_or_no_dialog = YesOrNoDialog(
                    self.main_window,
                    "Change output path",
                    "Do you want to change output path to selected directory?",
                    "Label files will be loaded and saved in this directory.",
                )
                result = yes_or_no_dialog.exec_()

                if result == QDialog.Accepted:
                    self.select_output_path(directory)

            self.load_image(self.images[0])

        # self.manage_labels()

    def open_file(self):
        file_dialog = QFileDialog()

        file_paths, _ = file_dialog.getOpenFileNames(
            None, "Select images", "", "Image Files (*.jpg *.jpeg *.png *.tif)"
        )

        if file_paths:
            self.images = file_paths
            self.images_list.clear()
            self.images_list.addItems(
                [os.path.basename(image) for image in self.images]
            )

            if self.output_path_line_edit.text() == "":
                self.select_output_path(os.path.dirname(file_paths[0]))
            else:
                yes_or_no_dialog = YesOrNoDialog(
                    self.main_window,
                    "Change output path",
                    "Do you want to change output path to directory with selected images?",
                    "Label files will be loaded and saved in this directory.",
                )
                result = yes_or_no_dialog.exec_()

                if result == QDialog.Accepted:
                    self.select_output_path(os.path.dirname(file_paths[0]))

            self.load_image(self.images[0])

    def load_classes_from_directory(self, directory):
        classes_file = os.path.join(directory, "classes.txt")
        if os.path.exists(classes_file):
            if self.labels_names:
                yes_no_dialog = YesOrNoDialog(
                    self.main_window,
                    "Load classes",
                    "Do you want to load class names from selected directory?",
                    "Current class names will be overwritten.",
                )
                result = yes_no_dialog.exec_()
                if result == QMessageBox.Accepted:
                    with open(classes_file, "r") as file:
                        self.labels_names = [
                            label.strip() for label in file.read().splitlines()
                        ]
                        self.label_name_selector.clear()
                        self.update_labels_names()
                else:
                    return
            else:
                with open(classes_file, "r") as file:
                    self.labels_names = [
                        label.strip() for label in file.read().splitlines()
                    ]
                    self.update_labels_names()

    def select_output_path(self, output_path=None):
        if output_path:
            directory = output_path
        else:
            file_dialog = QFileDialog()
            directory = file_dialog.getExistingDirectory(
                None, "Select output directory", ""
            )

        if directory:
            os.makedirs(directory, exist_ok=True)
            self.output_path_line_edit.setText(directory)
            self.image_view.output_path = directory
            self.load_classes_from_directory(directory)

    def delete_selected_photos(self):
        selected_items = self.images_list.selectedItems()
        selected_images = [item.text() for item in selected_items]
        images_to_delete = [
            image for image in self.images if os.path.basename(image) in selected_images
        ]
        for image in images_to_delete:
            self.images.remove(image)

        self.images_list.clear()
        self.images_list.addItems([os.path.basename(image) for image in self.images])

    def delete_selected_labels(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]
        rectangles_to_delete = [
            rectangle
            for rectangle in self.image_view.labels
            if rectangle.label_name in selected_labels
        ]
        self.image_view.delete_selected_rectangles(rectangles_to_delete)

    def set_saved(self, status):
        if status:
            self.status_label.setText("Saved")
            self.status_label.setStyleSheet("color: lime; font-weight: bold;")
            self.saved = True

        else:
            self.status_label.setText("Not saved")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")
            self.saved = False

    def update_labels_list(self, *args):
        self.labels_list.clear()
        labels = [rectangle.label_yolo for rectangle in self.image_view.labels]

        self.set_saved(labels == self.image_view.current_saved_labels)

        for rectangle in self.image_view.labels:
            self.labels_list.addItem(rectangle.label_name)

    def update_selection(self):
        for rectangle in self.image_view.labels:
            if rectangle.isSelected():
                self.labels_list.findItems(rectangle.label_name, Qt.MatchExactly)[
                    0
                ].setSelected(True)
            else:
                self.labels_list.findItems(rectangle.label_name, Qt.MatchExactly)[
                    0
                ].setSelected(False)

    def select_labels_from_list(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]

        self.image_view.select_labels(selected_labels)

    def set_select_mode(self):
        self.select_button.setChecked(True)
        self.polygon_button.setChecked(False)
        self.rectangle_button.setChecked(False)
        self.image_view.set_select_mode()

    def set_rect_selection(self):
        self.select_button.setChecked(False)
        self.polygon_button.setChecked(False)
        self.rectangle_button.setChecked(True)
        self.image_view.set_rect_selection()

    def set_polygon_selection(self):
        self.select_button.setChecked(False)
        self.rectangle_button.setChecked(False)
        self.polygon_button.setChecked(True)
        self.image_view.set_polygon_selection()

    def previous_image(self):
        current_image = self.image_view.url
        if current_image:
            current_image_index = self.images.index(current_image)
            if current_image_index > 0:
                self.load_image(self.images[current_image_index - 1])

    def next_image(self):
        current_image = self.image_view.url
        if current_image:
            current_image_index = self.images.index(current_image)
            if current_image_index < len(self.images) - 1:
                self.load_image(self.images[current_image_index + 1])

    def save_labels(self):
        output_path = self.output_path_line_edit.text()
        label_names = self.labels_names

        if output_path == "":
            self.select_output_path()
            return
        os.makedirs(output_path, exist_ok=True)

        output_label_path = os.path.join(
            output_path,
            os.path.splitext(os.path.basename(self.image_view.url))[0] + ".txt",
        )
        try:
            labels = [rectangle.label_yolo for rectangle in self.image_view.labels]

            with open(output_label_path, "w") as file:
                for label in labels:
                    file.write(f"{label}\n")
                    print(label)

            classes_file = os.path.join(output_path, "classes.txt")
            with open(classes_file, "w") as file:
                for label_name in label_names:
                    file.write(f"{label_name}\n")

            self.image_view.current_saved_labels = labels
            self.set_saved(labels == self.image_view.current_saved_labels)

        except Exception as e:
            print(e)

    def count_labels(self, path):
        label_file = os.path.join(
            self.output_path_line_edit.text(),
            os.path.splitext(os.path.basename(path))[0] + ".txt",
        )

        if os.path.exists(label_file):
            labels_count_dialog = LabelsCountDialog(
                self.main_window, self.labels_names, [label_file]
            )
            labels_count_dialog.exec_()

    def count_all_labels(self):
        label_files = [
            os.path.join(
                self.output_path_line_edit.text(),
                os.path.splitext(os.path.basename(image))[0] + ".txt",
            )
            for image in self.images
        ]

        label_files = [
            label_file for label_file in label_files if os.path.exists(label_file)
        ]

        if label_files:
            labels_count_dialog = LabelsCountDialog(
                self.main_window, self.labels_names, label_files
            )
            labels_count_dialog.exec_()
