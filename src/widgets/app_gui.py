import os

from PySide6.QtCore import QSize, Qt, QEvent, QModelIndex, QItemSelectionModel
from PySide6.QtGui import QAction, QIcon, QPixmap
from PySide6.QtWidgets import (
    QVBoxLayout,
    QHBoxLayout,
    QWidget,
    QToolBar,
    QListWidget,
    QLabel,
    QPushButton,
    QComboBox,
    QMenu,
    QMenuBar,
)

from src.utils.constants import *
from src.models.anno_project import AnnoProject
from src.models.label_image import LabelImage
from src.widgets.image_view import ImageView
from src.widgets.dialogs.labels_manage_dialog import LabelsManageDialog
from src.widgets.list_widget import ListWidget
from src.widgets.labels.rectangle_item import RectangleItem
from src.widgets.two_line_list_item import TwoLineListItem


class AppGui(QVBoxLayout):
    def __init__(self, anno_project: AnnoProject, parent=None):
        super(AppGui, self).__init__(parent)
        self.main_window = parent
        self.anno_project = anno_project

        self.setContentsMargins(0, 0, 0, 0)

        # Menu bar
        self.menu_bar = QMenuBar()
        self.file_menu = self.menu_bar.addMenu("File")
        self.new_project_action = QAction("New Project", self)
        self.new_project_action.triggered.connect(self.main_window.new_project)
        self.file_menu.addAction(self.new_project_action)
        self.load_project_action = QAction("Load Project", self)
        self.load_project_action.triggered.connect(self.main_window.load_project)
        self.file_menu.addAction(self.load_project_action)
        self.save_project_action = QAction("Save Project", self)
        self.save_project_action.triggered.connect(self.save_project)
        self.file_menu.addAction(self.save_project_action)
        self.file_menu.addSeparator()
        self.exit_action = QAction("Exit", self)
        self.exit_action.triggered.connect(self.main_window.close)
        self.file_menu.addAction(self.exit_action)

        self.project_menu = self.menu_bar.addMenu("Project")
        self.count_all_labels_action = QAction("Count all labels", self)
        self.count_all_labels_action.triggered.connect(self.count_all_labels)
        self.project_menu.addAction(self.count_all_labels_action)
        self.convert_project_action = QAction("Convert project", self)
        self.convert_project_action.triggered.connect(self.convert_project)
        self.project_menu.addAction(self.convert_project_action)

        self.help_menu = self.menu_bar.addMenu("Help")
        self.about_action = QAction("About", self)
        self.about_action.triggered.connect(self.main_window.show_about_dialog)
        self.help_menu.addAction(self.about_action)

        self.setMenuBar(self.menu_bar)

        # Top bar with app name and combobox with annotation types
        self.top_bar = QWidget()
        self.top_bar.setStyleSheet("padding: 5px;")
        self.top_bar_layout = QHBoxLayout()
        self.top_bar_layout.setContentsMargins(0, 0, 0, 0)

        self.app_logo = QLabel()
        self.app_logo.setPixmap(
            QPixmap(ICON_PATH).scaled(
                LOGO_SIZE, LOGO_SIZE, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

        self.app_name = QLabel(TITLE)
        self.app_name.setStyleSheet("font-size: 15px;")

        self.label_name_selector = QComboBox()
        self.label_name_selector.addItems(self.anno_project.class_names)
        self.label_name_selector.setFixedWidth(100)
        self.label_name_selector.currentTextChanged.connect(self.set_label_name)

        self.top_bar_layout.addSpacing(8)
        self.top_bar_layout.addWidget(self.app_logo)
        self.top_bar_layout.addWidget(self.app_name)
        self.top_bar_layout.addStretch()
        self.top_bar_layout.addWidget(self.label_name_selector)
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
        if self.anno_project.dataset_type == "YOLO":
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
        self.save_button.triggered.connect(self.save_project)
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
        self.image_view.labels_updated.connect(self.update_project)
        self.image_view.drawing_label.connect(self.update_box_size_label)
        self.image_view.on_image_loaded.connect(self.load_labels)
        self.image_view.scene().selectionChanged.connect(self.update_selection)

        self.center_layout.addWidget(self.image_view)

        self.right_panel_layout = QVBoxLayout()

        self.images_label = QLabel("Images")
        self.images_list = ListWidget()
        self.images_list.setSelectionMode(QListWidget.ExtendedSelection)
        self.images_list.setMaximumWidth(RIGHT_MAXW)
        self.images_list.doubleClicked.connect(self.load_image)
        self.images_list.installEventFilter(self)
        self.images_list.delete_pressed.connect(self.delete_selected_photos)

        self.labels_label = QLabel("Labels")
        self.labels_list = ListWidget()
        self.labels_list.setSelectionMode(QListWidget.SingleSelection)
        self.labels_list.setMaximumWidth(RIGHT_MAXW)
        self.labels_list.itemSelectionChanged.connect(self.select_labels_from_list)
        self.labels_list.installEventFilter(self)
        self.labels_list.delete_pressed.connect(self.delete_selected_labels)

        self.manage_labels_button = QPushButton("Manage labels")
        self.manage_labels_button.setToolTip("Add or delete label names")
        self.manage_labels_button.clicked.connect(self.manage_labels)

        self.right_panel_layout.addWidget(self.images_label)
        self.right_panel_layout.addWidget(self.images_list)
        self.right_panel_layout.addSpacing(10)
        self.right_panel_layout.addWidget(self.labels_label)
        self.right_panel_layout.addWidget(self.labels_list)
        self.right_panel_layout.addWidget(self.manage_labels_button)

        self.main_layout.addWidget(self.left_toolbar)
        self.main_layout.addLayout(self.center_layout)
        self.main_layout.addLayout(self.right_panel_layout)

        self.status_bar = QWidget()
        self.status_bar.setStyleSheet("padding: 5px;")
        self.status_bar.setContentsMargins(0, 0, 0, 0)
        self.status_bar_layout = QHBoxLayout()
        self.status_bar_layout.setContentsMargins(0, 0, 0, 0)
        self.version = QLabel(f"{TITLE} {VERSION}")
        self.status_label = QLabel("Saved")
        self.check_if_saved()
        self.box_size_label = QLabel("")

        self.status_bar_layout.addWidget(self.version)
        self.status_bar_layout.addStretch()
        self.status_bar_layout.addWidget(self.box_size_label)
        self.status_bar_layout.addWidget(self.status_label)

        self.status_bar.setLayout(self.status_bar_layout)

        self.addSpacing(5)
        self.addWidget(self.top_bar)
        self.addLayout(self.main_layout)
        self.addWidget(self.status_bar)
        self.addSpacing(5)

        self.update_image_list()
        self.set_select_mode()
        try:
            self.set_label_name(self.anno_project.class_names[0])
        except IndexError:
            pass

    def eventFilter(self, source, event):
        if event.type() == QEvent.ContextMenu and source is self.labels_list:
            item = source.itemAt(event.pos())
            menu = QMenu()

            if item is not None:
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
                menu.addAction("Load image")
                menu.addAction("Count labels")
                selected_menu = menu.exec_(event.globalPos())
                if selected_menu is None:
                    return True
                elif selected_menu.text() == "Load image":
                    self.load_image(
                        self.anno_project.images[self.images_list.row(item)]
                    )
                elif selected_menu.text() == "Count labels":
                    self.count_labels(
                        self.anno_project.images[self.images_list.row(item)]
                    )

            return True
        return super(QVBoxLayout, self).eventFilter(source, event)

    def convert_project(self):
        pass

    def update_image_list(self):
        """
        Updates image list widget with images from project
        """
        self.images_list.clear()
        for image in self.anno_project.images:
            item_widget = TwoLineListItem(image.name, os.path.dirname(image.path))
            item_widget.add_to_list(self.images_list)

    def load_image(self, image: LabelImage or QModelIndex):
        """
        Loads image to image viewer
        :type image: LabelImage
        """
        if type(image) is QModelIndex:
            label_image = self.anno_project.images[image.row()]
            self.anno_project.set_current_image(label_image)
            self.image_view.load_image(label_image)
            self.images_list.setCurrentRow(image.row())

        elif type(image) is LabelImage:
            self.anno_project.set_current_image(image)
            self.image_view.load_image(image)

    def load_labels(self):
        """
        Loads labels from current image to image viewer
        """
        self.image_view.load_labels(self.anno_project.current_image.labels)

    def update_project(self):
        """
        Updates project with current labels from image viewer
        """
        self.anno_project.current_image.labels = [
            item.to_dict() for item in self.image_view.current_labels
        ]
        self.check_if_saved()

        self.labels_list.clear()
        for item in self.image_view.current_labels:
            list_widget = TwoLineListItem(
                item.label_name,
                "Rectangle" if isinstance(item, RectangleItem) else "Polygon",
            )
            list_widget.add_to_list(self.labels_list)

    def check_if_saved(self):
        if self.anno_project.is_saved():
            self.status_label.setText("Saved")
            self.status_label.setStyleSheet("color: lime; font-weight: bold;")
        else:
            self.status_label.setText("Not saved")
            self.status_label.setStyleSheet("color: red; font-weight: bold;")

    def update_box_size_label(self, box_size: tuple, drawing: bool):
        if not drawing:
            self.box_size_label.setText("")
        else:
            self.box_size_label.setText(
                f"{round(box_size[0], 2), round(box_size[1], 2)}"
            )

    def set_label_name(self, label_name):
        self.image_view.label_name = label_name
        try:
            index = 0
            for i, name in enumerate(self.anno_project.class_names):
                if name == label_name:
                    index = i
                    break
            self.image_view.label_id = index
        except ValueError:
            self.image_view.label_id = None

    def save_project(self):
        self.anno_project.save_project()
        self.check_if_saved()

    def manage_labels(self):
        labels_manage_dialog = LabelsManageDialog(
            self.main_window, self.anno_project.class_names
        )
        labels_manage_dialog.exec_()
        self.anno_project.class_names = [
            labels_manage_dialog.list_widget.item(i).text()
            for i in range(labels_manage_dialog.list_widget.count())
        ]

        self.label_name_selector.clear()
        self.label_name_selector.addItems(self.anno_project.class_names)
        self.image_view.update_label_names()
        self.update_project()

    def delete_selected_photos(self):
        selected_items = self.images_list.selectedItems()
        selected_images = [item.text() for item in selected_items]
        images_to_delete = [
            image
            for image in self.anno_project.images
            if os.path.basename(image) in selected_images
        ]
        for image in images_to_delete:
            self.anno_project.images.remove(image)

        self.images_list.clear()
        self.images_list.addItems([image.name for image in self.anno_project.images])

    def delete_selected_labels(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]
        labels_to_delete = [
            label
            for label in self.image_view.current_labels
            if label.label_name in selected_labels
        ]
        self.image_view.delete_rectangles(labels_to_delete)

    def update_selection(self):
        for item in self.image_view.current_labels:
            for index in range(self.labels_list.count()):
                list_item = self.labels_list.item(index)
                widget = self.labels_list.itemWidget(list_item)
                if isinstance(widget, TwoLineListItem):
                    if widget and widget.title == item.label_name:
                        self.labels_list.setCurrentItem(list_item, QItemSelectionModel.Select)

    def select_labels_from_list(self):
        selected_items = self.labels_list.selectedItems()
        selected_labels = [item.text() for item in selected_items]

        self.image_view.select_labels(selected_labels)

    def set_select_mode(self):
        self.select_button.setChecked(True)
        self.polygon_button.setChecked(False)
        self.rectangle_button.setChecked(False)
        self.image_view.set_mode("select")

    def set_rect_selection(self):
        self.select_button.setChecked(False)
        self.polygon_button.setChecked(False)
        self.rectangle_button.setChecked(True)
        self.image_view.set_mode("rect_selection")

    def set_polygon_selection(self):
        self.select_button.setChecked(False)
        self.rectangle_button.setChecked(False)
        self.polygon_button.setChecked(True)
        self.image_view.set_mode("polygon_selection")

    def previous_image(self):
        current_image = self.anno_project.current_image
        if current_image:
            current_image_index = self.anno_project.images.index(current_image)
            if current_image_index > 0:
                self.load_image(self.anno_project.images[current_image_index - 1])

    def next_image(self):
        current_image = self.anno_project.current_image
        if current_image:
            current_image_index = self.anno_project.images.index(current_image)
            if current_image_index < len(self.anno_project.images) - 1:
                self.load_image(self.anno_project.images[current_image_index + 1])

    def count_labels(self, path):
        pass

    def count_all_labels(self):
        pass
