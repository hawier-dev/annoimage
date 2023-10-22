import os

from PySide6 import QtWidgets
from PySide6.QtCore import QSize, Qt, QEvent
from PySide6.QtGui import QAction, QIcon, QShortcut, QKeySequence, QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QFileDialog,
    QToolBar, QListWidget, QLabel, QPushButton, QSplitter, QStatusBar,
)

from constants import *
from widgets.image_view import ImageView


class AppGui(QVBoxLayout):
    def __init__(self, parent=None):
        super(AppGui, self).__init__(parent)
        self.main_window = parent
        self.images = []

        self.setContentsMargins(0, 0, 0, 0)

        # Top bar with app name and qcombobox with annotation types
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("padding: 5px;")
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.app_logo = QLabel()
        self.app_logo.setPixmap(QPixmap("icons/annoimage.png").scaled(24, 24, Qt.KeepAspectRatio, Qt.SmoothTransformation))

        self.app_name = QLabel(TITLE)
        self.app_name.setStyleSheet("font-size: 15px;")

        self.open_directory_button = QPushButton("Open directory")
        self.open_directory_button.clicked.connect(self.open_directory)

        self.open_file_button = QPushButton("Open file")
        self.open_file_button.clicked.connect(self.open_file)

        self.top_bar_layout.addWidget(self.app_logo)
        self.top_bar_layout.addWidget(self.app_name)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.open_directory_button)
        self.top_bar_layout.addWidget(self.open_file_button)

        self.top_bar.setLayout(self.top_bar_layout)

        # Main widget with image viewer and toolbar
        self.main_layout = QHBoxLayout()
        self.main_layout.setContentsMargins(0, 0, 0, 0)
        self.main_layout.setSpacing(5)

        # Left toolbar
        self.left_toolbar = QToolBar("Tools")
        self.left_toolbar.setIconSize(QSize(18, 18))
        self.left_toolbar.setMovable(False)
        self.left_toolbar.setOrientation(Qt.Vertical)

        self.select_button = QAction(QIcon("icons/select.png"), "Select (S)", self)
        self.select_button.triggered.connect(self.set_select_mode)
        self.select_button.setCheckable(True)
        self.select_button.setChecked(True)
        self.select_button.setShortcut("S")

        self.rectangle_button = QAction(QIcon("icons/rect_selection.png"), "Rectangle (R)", self)
        self.rectangle_button.triggered.connect(self.set_rect_selection)
        self.rectangle_button.setCheckable(True)
        self.rectangle_button.setShortcut("R")

        self.previous_button = QAction(QIcon("icons/previous.png"), "Previous (Arrow Left)", self)
        self.previous_button.triggered.connect(self.previous_image)
        self.previous_button.setShortcut("Left")

        self.next_button = QAction(QIcon("icons/next.png"), "Next (Arrow Right)", self)
        self.next_button.triggered.connect(self.next_image)
        self.next_button.setShortcut("Right")

        self.save_button = QAction(QIcon("icons/save.png"), "Save (CTRL + S)", self)
        self.save_button.triggered.connect(self.save_labeled_image)
        self.save_button.setShortcut("CTRL+S")

        self.left_toolbar.addAction(self.select_button)
        self.left_toolbar.addAction(self.rectangle_button)
        self.left_toolbar.addAction(self.previous_button)
        self.left_toolbar.addAction(self.next_button)
        self.left_toolbar.addAction(self.save_button)

        # Center widget with image viewer
        self.center_layout = QVBoxLayout()

        self.image_view = ImageView()
        self.image_view.label_added.connect(self.update_labels_list)
        self.image_view.updated_labels.connect(self.update_labels_list)
        self.image_view.scene().selectionChanged.connect(self.update_selection)

        self.center_layout.addWidget(self.image_view)

        self.right_panel_layout = QVBoxLayout()

        self.labels_label = QLabel("Labels")
        self.labels_list = QListWidget()
        self.labels_list.setMaximumWidth(150)
        self.labels_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.labels_list.itemSelectionChanged.connect(self.select_labels_from_list)
        self.labels_list.installEventFilter(self)

        self.images_label = QLabel("Images")
        self.images_list = QListWidget()
        self.images_list.setMaximumWidth(150)
        self.images_list.doubleClicked.connect(self.load_image)
        self.images_list.installEventFilter(self)

        self.right_panel_layout.addWidget(self.labels_label)
        self.right_panel_layout.addWidget(self.labels_list)
        self.right_panel_layout.addSpacing(10)
        self.right_panel_layout.addWidget(self.images_label)
        self.right_panel_layout.addWidget(self.images_list)

        self.main_layout.addWidget(self.left_toolbar)
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.right_panel_layout)

        self.status_bar = QStatusBar()
        self.version = QLabel(f"{TITLE} {VERSION}")
        self.status_bar.addWidget(self.version)

        self.main_window.setStatusBar(self.status_bar)

        self.addWidget(self.top_bar)
        self.addLayout(self.main_layout)

        # self.main_window.addToolBar(Qt.LeftToolBarArea, self.left_toolbar)
        self.setup_shortcuts()

    def eventFilter(self, source, event):
        if (event.type() == QEvent.ContextMenu and
                source is self.labels_list):
            menu = QtWidgets.QMenu()
            menu.addAction('Zoom to')
            item = source.itemAt(event.pos())
            if item is not None:
                selected_menu = menu.exec_(event.globalPos())
                if selected_menu is None:
                    return True
                elif selected_menu.text() == 'Zoom to':
                    self.image_view.zoom_to_rect(item.text())

            return True
        return super(QVBoxLayout, self).eventFilter(source, event)

    def setup_shortcuts(self):
        delete_shortcut = QShortcut(QKeySequence(Qt.Key_Delete), self.main_window)
        delete_shortcut.activated.connect(self.delete_selected_labels)

    def load_image(self, image):
        # load image by index from images list
        self.image_view.load_image(self.images[image.row()])

    def open_directory(self):
        file_dialog = QFileDialog()

        directory = file_dialog.getExistingDirectory(
            None, "Select directory with images", ""
        )

        if directory:
            self.images = [os.path.join(directory, file) for file in os.listdir(directory) if file.endswith(".jpg")]
            self.images_list.clear()
            self.images_list.addItems([os.path.basename(image) for image in self.images])

    def open_file(self):
        pass

    def delete_selected_labels(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]
        rectangles_to_delete = [rectangle for rectangle in self.image_view.rectangles if rectangle.label_name in selected_labels]
        self.image_view.delete_selected_rectangles(rectangles_to_delete)

    def update_labels_list(self):
        self.labels_list.clear()
        for rectangle in self.image_view.rectangles:
            self.labels_list.addItem(rectangle.label_name)

    def update_selection(self):
        for rectangle in self.image_view.rectangles:
            if rectangle.isSelected():
                self.labels_list.findItems(rectangle.label_name, Qt.MatchExactly)[0].setSelected(True)
            else:
                self.labels_list.findItems(rectangle.label_name, Qt.MatchExactly)[0].setSelected(False)

    def select_labels_from_list(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]

        self.image_view.select_labels(selected_labels)

    def set_select_mode(self):
        self.select_button.setChecked(True)
        self.rectangle_button.setChecked(False)
        self.image_view.set_select_mode()

    def set_rect_selection(self):
        self.select_button.setChecked(False)
        self.rectangle_button.setChecked(True)
        self.image_view.set_rect_selection()

    def previous_image(self):
        pass

    def next_image(self):
        pass

    def save_labeled_image(self):
        file_dialog = QFileDialog()
        file_dialog.setNameFilter("JPEG Image Files (*.jpg)")

        file_path, _ = file_dialog.getSaveFileName(
            None, "Save Comparison Screenshot", "", "JPEG Image Files (*.jpg)"
        )

        if file_path:
            screenshot = self.main_widget.grab()
            screenshot.save(file_path, "jpg")
            print(f"Saved screenshot as {file_path}")
