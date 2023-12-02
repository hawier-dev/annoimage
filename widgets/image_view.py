import os

from PIL import Image
from PySide6.QtCore import QRectF, QPointF, Qt, Signal, QEvent
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
    QGraphicsRectItem,
    QLabel,
    QDialog,
)
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QPainter, QMouseEvent,
)

from constants import SURFACE_COLOR
from widgets.add_label_dialog import AddLabelDialog
from widgets.image_loader import ImageLoader
from widgets.rectangle_item import RectangleItem

Image.MAX_IMAGE_PIXELS = 933120000


class ImageView(QGraphicsView):
    label_added = Signal(list)
    updated_labels = Signal(list)
    drawing_rectangle = Signal(tuple, bool)
    on_image_loaded = Signal(str)

    def __init__(self, parent=None):
        super().__init__()
        self.zoom_factor = 0
        self.url = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rect_item = None
        self.rectangles = []
        self.current_saved_labels = []
        self.label_name = None
        self.label_id = None
        self.labels_names = []

        self.parent = parent
        self.loading_image = False
        self.setContentsMargins(5, 5, 5, 5)

        self.current_mode = "select"

        self.image_width = 0
        self.image_height = 0

        self.setScene(QGraphicsScene(self))
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

        self.horizontalScrollBar().setFixedHeight(10)
        self.verticalScrollBar().setFixedWidth(10)

        self.image_label = QLabel(self)
        self.image_label.setAlignment(Qt.AlignCenter)
        self.image_label.setText("No image loaded")
        self.image_label.setStyleSheet("font-size: 18px; color: white;")

        self.loading_label = QLabel(self)
        self.loading_label.setAlignment(Qt.AlignCenter)
        self.loading_label.setText("Loading...")
        self.loading_label.setStyleSheet(
            f"font-size: 18px; color: white; padding: 10px; background-color: {SURFACE_COLOR};"
        )
        self.loading_label.setVisible(False)

        # self.scene().addWidget(self.image_label)
        # self.scene().addWidget(self.loading_label)

    def dragEnterEvent(self, event: QDragEnterEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            event.acceptProposedAction()

    def dropEvent(self, event: QDropEvent):
        mime_data = event.mimeData()
        if mime_data.hasUrls():
            file_path = mime_data.urls()[0].toLocalFile()
            self.load_image(file_path)

    def dragMoveEvent(self, event):
        event.accept()

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1 / 1.1

        self.zoom_factor *= zoom_factor
        self.scale(zoom_factor, zoom_factor)

    def load_image(self, file_path):
        if self.loading_image:
            return

        self.image_label.setVisible(False)
        self.loading_image = True
        self.loading_label.move(
            self.width() // 2 - self.loading_label.width() // 2,
            self.height() // 2 - self.loading_label.height() // 2,
        )
        self.loading_label.setVisible(True)
        self.url = file_path

        self.image_loader = ImageLoader(file_path)
        self.image_loader.loaded.connect(self.image_loaded)
        self.image_loader.start()

    def image_loaded(self, pixmap):
        self.loading_image = False
        if pixmap.width() == 0:
            QMessageBox.critical(
                self, "Error", "Unable to load the image.", QMessageBox.Ok
            )
            self.loading_label.setVisible(False)
            return

        self.scene().clear()
        self.scene().addPixmap(pixmap)
        self.image_width = pixmap.width()
        self.image_height = pixmap.height()

        self.fitInView(self.scene().items()[0], Qt.KeepAspectRatio)
        self.scene().setSceneRect(0, 0, self.image_width, self.image_height)

        self.rectangles = []
        self.current_saved_labels = []
        self.load_labels()

        self.updated_labels.emit(self.rectangles)
        self.on_image_loaded.emit(self.url)

        self.image_label.setVisible(False)
        self.loading_label.setVisible(False)

    def update_label_names(self):
        for rectangle in self.rectangles:
            rectangle.label_name = (
                self.labels_names[int(rectangle.label_id)]
                + " "
                + rectangle.label_name.split(" ")[-1]
            )

    def load_labels(self):
        labels_file_path = os.path.splitext(self.url)[0] + ".txt"
        if os.path.exists(labels_file_path):
            with open(labels_file_path, "r") as labels_file:
                for line in labels_file.readlines():
                    line = line.strip()
                    label_id, x, y, w, h = line.split(" ")
                    x, y, width, height = (
                        float(x) * self.image_width,
                        float(y) * self.image_height,
                        float(w) * self.image_width,
                        float(h) * self.image_height,
                    )
                    for i in range(int(label_id) + 1):
                        try:
                            self.labels_names[i]
                        except IndexError:
                            self.parent.labels_names.append(f"Unknown_{i}")
                            self.parent.update_labels_names()

                    label_name = self.generate_label_name(
                        self.labels_names[int(label_id)]
                    )
                    rectangle = RectangleItem(
                        QPointF(x - width / 2, y - height / 2),
                        QPointF(x + width / 2, y + height / 2),
                        label_name,
                        label_id,
                        self.image_width,
                        self.image_height,
                        self,
                    )
                    if self.current_mode == "select":
                        rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, True)
                        rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

                    self.rectangles.append(rectangle)
                    self.current_saved_labels.append(line)
                    self.scene().addItem(rectangle)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_mode == "rect_selection":
            self.start_point = self.mapToScene(event.pos())
            self.drawing = (
                0 <= self.start_point.x() <= self.image_width
                and 0 <= self.start_point.y() <= self.image_height
            )
        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ClosedHandCursor)
            self.movable_disable()
            press_event = QMouseEvent(QEvent.GraphicsSceneMousePress, event.pos(), Qt.LeftButton, Qt.LeftButton, Qt.NoModifier)
            self.mousePressEvent(press_event)


        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            self.draw_rectangle()

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            self.draw_rectangle()
            self.drawing = False

            rectangle_item = RectangleItem(
                self.start_point,
                self.end_point,
                self.generate_label_name(self.label_name),
                self.label_id,
                self.image_width,
                self.image_height,
                self,
            )

            if self.current_mode == "select":
                rectangle_item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
                rectangle_item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

            if rectangle_item.rect().width() < 5 or rectangle_item.rect().height() < 5:
                self.scene().removeItem(rectangle_item)
                self.scene().removeItem(self.rect_item)
                return

            if not self.labels_names:
                add_label_dialog = AddLabelDialog()
                if add_label_dialog.exec() == QDialog.Accepted:
                    self.label_name = add_label_dialog.label_name_input.text()
                    self.label_id = 0
                    self.labels_names.append(self.label_name)
                    self.parent.labels_names.append(self.label_name)
                    self.parent.label_name_selector.addItem(self.label_name)
                    self.parent.label_name_selector.setCurrentText(self.label_name)
                    rectangle_item.label_name = self.generate_label_name(
                        self.label_name
                    )
                    rectangle_item.label_id = self.label_id
                    rectangle_item.label_line = rectangle_item.create_yolo_label()

                else:
                    self.scene().removeItem(self.rect_item)
                    return

            self.rectangles.append(rectangle_item)
            self.scene().addItem(rectangle_item)
            if self.rect_item in self.scene().items():
                self.scene().removeItem(self.rect_item)

            self.label_added.emit(self.rectangles)
            self.drawing_rectangle.emit(
                (rectangle_item.rect().width(), rectangle_item.rect().height()), False
            )

        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            if self.current_mode == "select":
                self.set_select_mode()

            elif self.current_mode == "rect_selection":
                self.set_rect_selection()

        super().mouseReleaseEvent(event)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_selected_rectangles(self.scene().selectedItems())

        elif event.key() == Qt.Key_Space:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ClosedHandCursor)
            self.movable_disable()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.NoDrag)
            if self.current_mode == "select":
                self.set_select_mode()
            elif self.current_mode == "rect_selection":
                self.set_rect_selection()

    def draw_rectangle(self):
        if self.rect_item in self.scene().items():
            self.scene().removeItem(self.rect_item)

        x1 = max(0, min(self.start_point.x(), self.image_width))
        y1 = max(0, min(self.start_point.y(), self.image_height))
        x2 = max(0, min(self.end_point.x(), self.image_width))
        y2 = max(0, min(self.end_point.y(), self.image_height))

        self.start_point = QPointF(x1, y1)
        self.end_point = QPointF(x2, y2)

        self.rect_item = RectangleItem(
            self.start_point,
            self.end_point,
            self.generate_label_name(self.label_name),
            self.label_id,
            self.image_width,
            self.image_height,
            self,
        )

        self.drawing_rectangle.emit(
            (
                round(self.rect_item.rect().width(), 2),
                round(self.rect_item.rect().height(), 2),
            ),
            True,
        )
        self.scene().addItem(self.rect_item)
        # self.rectangles.append(rect)

    def calculate_rectangle(self):
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        return QRectF(
            QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2))
        )

    def set_select_mode(self):
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.ArrowCursor)
        self.current_mode = "select"

        self.movable_enable()

    def set_rect_selection(self):
        self.setDragMode(QGraphicsView.NoDrag)
        self.setCursor(Qt.CrossCursor)
        self.current_mode = "rect_selection"

        self.movable_disable()

    def generate_label_name(self, label_str):
        label_names = [rectangle.label_name for rectangle in self.rectangles]
        i = 0
        while True:
            label_name = f"{label_str} {i}"
            if label_name not in label_names:
                return label_name
            i += 1

    def delete_selected_rectangles(self, rectangles):
        for rectangle in rectangles:
            self.scene().removeItem(rectangle)
            self.rectangles.remove(rectangle)

        self.updated_labels.emit(self.rectangles)

    def select_labels(self, labels):
        for rectangle in self.rectangles:
            if rectangle.label_name in labels:
                rectangle.setSelected(True)
            else:
                rectangle.setSelected(False)

    def zoom_to_rect(self, label):
        for rectangle in self.rectangles:
            if rectangle.label_name == label:
                self.fitInView(rectangle, Qt.KeepAspectRatio)
                break

    def resizeEvent(self, event):
        super().resizeEvent(event)
        self.image_label.setGeometry(self.viewport().rect())

    def movable_disable(self):
        """
        Disable movable flag for all rectangles
        """
        for rectangle in self.rectangles:
            rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, False)
            rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, False)

    def movable_enable(self):
        """
        Enable movable flag for all rectangles
        """
        for rectangle in self.rectangles:
            rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, True)
            rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
