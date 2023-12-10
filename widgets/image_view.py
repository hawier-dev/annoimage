import datetime
import json
import os

from PIL import Image
from PySide6.QtCore import QRectF, QPointF, Qt, Signal, QEvent, QTimer
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
    QGraphicsRectItem,
    QLabel,
    QDialog,
    QGraphicsItem,
)
from PySide6.QtGui import (
    QDragEnterEvent,
    QDropEvent,
    QPainter,
    QMouseEvent,
    QPolygonF,
)

from constants import SURFACE_COLOR, TITLE, VERSION
from models.label_image import LabelImage
from widgets.add_label_dialog import AddLabelDialog
from widgets.polygon_item import PolygonItem
from widgets.rectangle_item import RectangleItem
from models.image_loader import ImageLoader

Image.MAX_IMAGE_PIXELS = 933120000


class ImageView(QGraphicsView):
    label_added = Signal()
    updated_labels = Signal(list)
    drawing_label = Signal(tuple, bool)
    on_image_loaded = Signal()

    def __init__(self, parent=None):
        super().__init__()
        self.zoom_factor = 0
        self.image_loader = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rect_item = None
        self.label_name = None
        self.label_id = None
        self.polygon_points = []
        self.polygon_item = None

        self.output_path = None

        # self.coco_dataset = {
        #     "info": {
        #         "description": "Dataset for image segmentation",
        #         "url": "",
        #         "version": "1.0",
        #         "year": 2021,
        #         "contributor": "",
        #         "date_created": datetime.datetime.now().strftime("%Y/%m/%d"),
        #         "creator": f"{TITLE} {VERSION}",
        #     },
        #     "licenses": [],
        #     "images": [],
        #     "annotations": [],
        #     "categories": [],
        # }

        self.timer = QTimer(self)
        self.timer.setSingleShot(True)

        self.parent = parent
        self.loading_image = False
        self.setContentsMargins(5, 5, 5, 5)

        self.current_mode = "select"

        self.image_width = 0
        self.image_height = 0

        self.setScene(QGraphicsScene(self))
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)
        self.setRubberBandSelectionMode(Qt.IntersectsItemShape)

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

    def load_image(self, label_image: LabelImage):
        if self.loading_image:
            return

        self.image_label.setVisible(False)
        self.loading_image = True
        self.loading_label.move(
            self.width() // 2 - self.loading_label.width() // 2,
            self.height() // 2 - self.loading_label.height() // 2,
        )
        self.loading_label.setVisible(True)

        self.image_loader = ImageLoader(label_image.path)
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

        self.on_image_loaded.emit()

        self.image_label.setVisible(False)
        self.loading_label.setVisible(False)

    def update_label_names(self):
        for item in self.parent.anno_project.current_image.labels:
            item.label_name = (
                self.parent.anno_project.class_names[int(item.label_name_id)]
                + " "
                + item.label_name.split(" ")[-1]
            )

    def get_label_id(self):
        label_id = 1
        for label in self.parent.anno_project.current_image.labels:
            if label.label_id == label_id:
                label_id += 1

        return label_id

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_mode == "select":
            item = self.itemAt(event.pos())
            if item:
                for i in self.scene().items():
                    i.setSelected(False)

        elif event.button() == Qt.LeftButton and self.current_mode == "rect_selection":
            self.start_point = self.mapToScene(event.pos())
            self.drawing = (
                0 <= self.start_point.x() <= self.image_width
                and 0 <= self.start_point.y() <= self.image_height
            )

        elif (
            event.button() == Qt.LeftButton and self.current_mode == "polygon_selection"
        ):
            self.drawing = True
            if not self.polygon_points:
                self.polygon_points.append(self.mapToScene(event.pos()))
            else:
                current_point = self.mapToScene(event.pos())
                self.polygon_points.append(current_point)

        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ClosedHandCursor)
            self.movable_disable()
            press_event = QMouseEvent(
                QEvent.GraphicsSceneMousePress,
                event.pos(),
                Qt.LeftButton,
                Qt.LeftButton,
                Qt.NoModifier,
            )
            self.mousePressEvent(press_event)

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing and self.current_mode == "rect_selection":
            self.end_point = self.mapToScene(event.pos())
            self.draw_rectangle()

        elif self.drawing and self.current_mode == "polygon_selection":
            current_point = self.mapToScene(event.pos())
            self.polygon_points[-1] = current_point
            self.draw_polygon()

        super().mouseMoveEvent(event)

    def process_item(self, item):
        if not self.parent.anno_project.class_names:
            add_label_dialog = AddLabelDialog(self)
            if add_label_dialog.exec() == QDialog.Accepted:
                self.label_name = add_label_dialog.label_name_input.text()
                self.label_id = 0
                self.parent.anno_project.class_names.append(self.label_name)
                self.parent.label_name_selector.addItem(self.label_name)
                self.parent.label_name_selector.setCurrentText(self.label_name)
                item.label_name = self.generate_label_name(self.label_name)
                item.label_name_id = self.label_id
            else:
                self.scene().removeItem(self.rect_item)
                return

        self.parent.anno_project.current_image.labels.append(item)
        self.scene().addItem(item)
        if isinstance(item, RectangleItem):
            size = (item.rect().width(), item.rect().height())
        elif isinstance(item, PolygonItem):
            size = (item.boundingRect().width(), item.boundingRect().height())
        else:
            raise ValueError("Unexpected item type")

        self.label_added.emit()
        self.drawing_label.emit(size, False)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            if self.current_mode == "rect_selection":
                self.draw_rectangle()
                self.drawing = False

                item = RectangleItem(
                    self.start_point,
                    self.end_point,
                    self.generate_label_name(self.label_name),
                    self.label_id,
                )

                if self.current_mode == "select":
                    item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
                    item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

                if item.rect().width() < 5 or item.rect().height() < 5:
                    self.scene().removeItem(item)
                    self.scene().removeItem(self.rect_item)
                    return

                self.process_item(item)
                self.scene().removeItem(self.rect_item)

            elif self.current_mode == "polygon_selection":
                double_click = False
                if not self.timer.isActive():
                    self.timer.start(200)
                else:
                    self.timer.stop()
                    double_click = True
                self.polygon_points.append(self.end_point)
                self.draw_polygon()

                if len(self.polygon_points) >= 3 and double_click:
                    # Call complete_polygon function
                    item = PolygonItem(
                        QPolygonF(self.polygon_points),
                        self.generate_label_name(self.label_name),
                        self.label_id,
                        self.image_width,
                        self.image_height,
                        self,
                    )
                    self.process_item(item)
                    self.scene().removeItem(self.polygon_item)
                    self.polygon_item = None
                    self.polygon_points = []

                    self.drawing = False

        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            if self.current_mode == "select":
                self.set_select_mode()

            elif self.current_mode == "rect_selection":
                self.set_rect_selection()

        super().mouseReleaseEvent(event)

    def draw_polygon(self):
        if self.polygon_item in self.scene().items():
            self.scene().removeItem(self.polygon_item)

        polygon_item = PolygonItem(
            QPolygonF(self.polygon_points),
            self.label_name,
            self.label_id,
            self.image_width,
            self.image_height,
            self,
        )
        self.scene().addItem(polygon_item)
        self.polygon_item = polygon_item

    def complete_polygon(self):
        polygon_item = PolygonItem(
            QPolygonF(self.polygon_points),
            self.generate_label_name(self.label_name),
            self.label_id,
            self.image_width,
            self.image_height,
            self,
        )
        self.parent.anno_project.current_image.labels.append(polygon_item)
        self.scene().addItem(polygon_item)

        self.scene().removeItem(self.polygon_item)
        self.polygon_item = None
        self.polygon_points = []

        self.label_added.emit()
        self.drawing_label.emit(
            (polygon_item.boundingRect().width(), polygon_item.boundingRect().height()),
            False,
        )

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
            elif self.current_mode == "polygon_selection":
                self.set_polygon_selection()

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
            temporary=True,
        )

        self.drawing_label.emit(
            (
                round(self.rect_item.rect().width(), 2),
                round(self.rect_item.rect().height(), 2),
            ),
            True,
        )
        self.scene().addItem(self.rect_item)

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

    def set_polygon_selection(self):
        self.setDragMode(QGraphicsView.NoDrag)
        self.setCursor(Qt.CrossCursor)
        self.current_mode = "polygon_selection"

        self.movable_disable()

    def generate_label_name(self, label_str):
        label_names = [item.label_name for item in self.parent.anno_project.current_image.labels]
        i = 0
        while True:
            label_name = f"{label_str} {i}"
            if label_name not in label_names:
                return label_name
            i += 1

    def delete_selected_rectangles(self, rectangles):
        for rectangle in rectangles:
            self.scene().removeItem(rectangle)
            self.labels.remove(rectangle)

        self.updated_labels.emit(self.labels)

    def select_labels(self, labels):
        for rectangle in self.labels:
            if rectangle.label_name in labels:
                rectangle.setSelected(True)
            else:
                rectangle.setSelected(False)

    def zoom_to_rect(self, label):
        for rectangle in self.parent.anno_project.current_image.labels:
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
        if self.parent.anno_project.current_image:
            for rectangle in self.parent.anno_project.current_image.labels:
                rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, False)
                rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, False)

    def movable_enable(self):
        """
        Enable movable flag for all rectangles
        """
        if self.parent.anno_project.current_image:
            for rectangle in self.parent.anno_project.current_image.labels:
                rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, True)
                rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
