from PIL import Image
from PySide6.QtCore import QPointF, Qt, Signal, QEvent, QTimer
from PySide6.QtWidgets import (
    QGraphicsView,
    QGraphicsScene,
    QMessageBox,
    QGraphicsRectItem,
    QLabel,
    QDialog,
)
from PySide6.QtGui import (
    QPainter,
    QMouseEvent,
    QPolygonF,
)

from src.utils.constants import SURFACE_COLOR
from src.models.label_image import LabelImage
from src.widgets.dialogs.add_label_dialog import AddLabelDialog
from src.widgets.labels.polygon_item import PolygonItem
from src.widgets.labels.rectangle_item import RectangleItem
from src.models.image_loader import ImageLoader

Image.MAX_IMAGE_PIXELS = 933120000


class ImageView(QGraphicsView):
    labels_updated = Signal()
    drawing_label = Signal(tuple, bool)
    on_image_loaded = Signal()

    def __init__(self, parent=None):
        super().__init__()
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
        self.current_labels = []

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

    def wheelEvent(self, event):
        zoom_in = event.angleDelta().y() > 0
        zoom_factor = 1.1 if zoom_in else 1 / 1.1

        self.scale(zoom_factor, zoom_factor)

    def load_image(self, label_image: LabelImage):
        """
        Load image from path
        :param label_image: LabelImage object
        """
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
        """
        Called when image is loaded
        :param pixmap: QPixmap object
        """
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

    def load_labels(self, labels):
        """
        Load labels from list
        :param labels: list of labels
        """
        self.current_labels = []
        for label in labels:
            if label["type"] == "RectangleItem":
                new_label = RectangleItem.from_dict(label, self)
                self.current_labels.append(new_label)
                self.scene().addItem(new_label)
            elif label["type"] == "PolygonItem":
                new_label = PolygonItem.from_dict(label, self)
                self.current_labels.append(new_label)
                self.scene().addItem(new_label)

        self.set_mode(self.current_mode)
        self.labels_updated.emit()

    def update_labels(self):
        self.labels_updated.emit()

    def update_label_names(self):
        """
        Update label names with class names from project
        """
        for item in self.current_labels:
            item.label_name = (
                self.parent.anno_project.class_names[int(item.label_name_id)]
                + " "
                + item.label_name.split(" ")[-1]
            )

        self.labels_updated.emit()

    def get_label_id(self):
        """
        Get next label id
        """
        label_id = 1
        for label in self.current_labels:
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
        """
        Process item after drawing is finished
        :param item: RectangleItem or PolygonItem
        """
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

        self.current_labels.append(item)
        self.scene().addItem(item)
        if isinstance(item, RectangleItem):
            size = (item.rect().width(), item.rect().height())
        elif isinstance(item, PolygonItem):
            size = (item.boundingRect().width(), item.boundingRect().height())
        else:
            raise ValueError("Unexpected item type")

        self.labels_updated.emit()
        self.drawing_label.emit(size, False)

    def mouseReleaseEvent(self, event):
        """
        Handle mouse release events for different selection modes.

        :param event: The QMouseEvent triggered on mouse release.
        """
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            if self.current_mode == "rect_selection":
                self.handle_rectangle_selection()
            elif self.current_mode == "polygon_selection":
                self.handle_polygon_selection()

        elif event.button() == Qt.MiddleButton:
            self.setDragMode(QGraphicsView.NoDrag)
            self.set_mode(self.current_mode)

        super().mouseReleaseEvent(event)

    def handle_rectangle_selection(self):
        """
        Handle the creation and processing of a rectangle selection.
        """
        self.draw_rectangle()
        self.drawing = False

        item = self.create_rectangle_item()
        if item.rect().width() < 5 or item.rect().height() < 5:
            self.remove_temporary_items()
            return

        self.process_item(item)
        self.remove_temporary_items()

    def handle_polygon_selection(self):
        """
        Handle the creation and processing of a polygon selection.
        """
        double_click = self.detect_double_click()
        self.polygon_points.append(self.end_point)
        self.draw_polygon()

        if len(self.polygon_points) >= 3 and double_click:
            self.complete_polygon()

    def create_rectangle_item(self):
        """
        Create and configure a RectangleItem based on the current selection.

        :return: The created RectangleItem.
        """
        item = RectangleItem(
            self,
            self.start_point,
            self.end_point,
            self.generate_label_name(self.label_name),
            self.label_id,
        )

        if self.current_mode == "select":
            item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
            item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

        return item

    def remove_temporary_items(self):
        """
        Remove temporary items from the scene.
        """
        self.scene().removeItem(self.rect_item)

    def detect_double_click(self):
        """
        Detect if a double-click event has occurred.

        :return: True if a double-click event is detected, False otherwise.
        """
        double_click = False
        if not self.timer.isActive():
            self.timer.start(200)
        else:
            self.timer.stop()
            double_click = True
        return double_click

    def draw_rectangle(self):
        """
        Draw rectangle
        Function is called when mouse is moved during drawing
        """
        if self.rect_item in self.scene().items():
            self.scene().removeItem(self.rect_item)

        x1 = max(0, min(self.start_point.x(), self.image_width))
        y1 = max(0, min(self.start_point.y(), self.image_height))
        x2 = max(0, min(self.end_point.x(), self.image_width))
        y2 = max(0, min(self.end_point.y(), self.image_height))

        self.start_point = QPointF(x1, y1)
        self.end_point = QPointF(x2, y2)

        self.rect_item = RectangleItem(
            self,
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

    def draw_polygon(self):
        """
        Draw polygon
        """
        if self.polygon_item in self.scene().items():
            self.scene().removeItem(self.polygon_item)

        polygon_item = PolygonItem(
            self,
            QPolygonF(self.polygon_points),
            self.label_name,
            self.label_id,
        )
        self.drawing_label.emit(
            (polygon_item.boundingRect().width(), polygon_item.boundingRect().height()),
            True,
        )

        self.scene().addItem(polygon_item)
        self.polygon_item = polygon_item

    def complete_polygon(self):
        """
        Complete polygon drawing and create PolygonItem.
        A polygon must have at least three points.
        """
        if len(self.polygon_points) < 3:
            return

        polygon_item = PolygonItem(
            self,
            QPolygonF(self.polygon_points),
            self.generate_label_name(self.label_name),
            self.label_id,
        )
        self.current_labels.append(polygon_item)
        self.scene().addItem(polygon_item)

        self.scene().removeItem(self.polygon_item)
        self.polygon_item = None
        self.polygon_points = []
        self.drawing = False
        self.drawing_label.emit(
            (polygon_item.boundingRect().width(), polygon_item.boundingRect().height()),
            False,
        )

        self.labels_updated.emit()

    def keyPressEvent(self, event):
        if event.key() == Qt.Key_Delete:
            self.delete_rectangles(self.scene().selectedItems())

        elif event.key() == Qt.Key_Space:
            self.setDragMode(QGraphicsView.ScrollHandDrag)
            self.setCursor(Qt.ClosedHandCursor)
            self.movable_disable()

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key_Space and not event.isAutoRepeat():
            self.setDragMode(QGraphicsView.NoDrag)
            self.set_mode(self.current_mode)

    def set_mode(self, mode):
        """
        Set the current mode for the ImageView.

        :param mode: A string representing the mode to be set.
                     Valid values are 'select', 'rect_selection', 'polygon_selection'.
        """
        if mode not in ["select", "rect_selection", "polygon_selection"]:
            raise ValueError(f"Invalid mode: {mode}")

        if mode == "select":
            self.setDragMode(QGraphicsView.RubberBandDrag)
            self.setCursor(Qt.ArrowCursor)
            self.movable_enable()
        else:
            self.setDragMode(QGraphicsView.NoDrag)
            self.setCursor(Qt.CrossCursor)
            self.movable_disable()

        self.current_mode = mode

    def generate_label_name(self, label_str):
        """
        Generate label name
        Label name is generated by adding number to the end of label_str
        :param label_str: label name
        """
        label_names = [item.label_name for item in self.current_labels]
        i = 0
        while True:
            label_name = f"{label_str} {i}"
            if label_name not in label_names:
                return label_name
            i += 1

    def delete_rectangles(self, labels):
        """
        Delete selected rectangles
        :param labels: list of labels
        """
        for item in labels:
            self.scene().removeItem(item)
            self.current_labels.remove(item)

        self.labels_updated.emit()

    def select_labels(self, labels):
        for item in self.current_labels:
            if item.label_name in labels:
                item.setSelected(True)
            else:
                item.setSelected(False)

    def zoom_to_rect(self, label):
        for rectangle in self.current_labels:
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
        for item in self.current_labels:
            item.setFlag(QGraphicsRectItem.ItemIsMovable, False)
            item.setFlag(QGraphicsRectItem.ItemIsSelectable, False)

    def movable_enable(self):
        """
        Enable movable flag for all items
        """
        for item in self.current_labels:
            item.setFlag(QGraphicsRectItem.ItemIsMovable, True)
            item.setFlag(QGraphicsRectItem.ItemIsSelectable, True)
