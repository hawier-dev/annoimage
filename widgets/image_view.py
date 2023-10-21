from PIL import Image
from PIL.ImageQt import ImageQt
from PySide6.QtCore import QRectF, QPointF, Qt, QLineF, QEvent, Signal
from PySide6.QtWidgets import QGraphicsView, QGraphicsScene, QMessageBox, QGraphicsRectItem
from PySide6.QtGui import (
    QPixmap,
    QDragEnterEvent,
    QDropEvent,
    QPainter, QPen, QBrush, QColor
)

from widgets.rectangle_item import RectangleItem

Image.MAX_IMAGE_PIXELS = 933120000


class ImageView(QGraphicsView):
    label_added = Signal(list)
    updated_labels = Signal(list)

    def __init__(self):
        super().__init__()
        self.zoom_factor = 0
        self.url = None
        self.drawing = False
        self.start_point = None
        self.end_point = None
        self.rect_item = None
        self.rectangles = []
        self.middle_mouse_button_pressed = False
        self.middle_mouse_last_position = None

        self.current_mode = "select"

        self.setScene(QGraphicsScene(self))
        self.setAcceptDrops(True)
        self.setRenderHint(QPainter.Antialiasing)
        self.setRenderHint(QPainter.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.AnchorUnderMouse)

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
        img = Image.open(file_path)
        img = ImageQt(img)
        pixmap = QPixmap.fromImage(img)
        if pixmap.width() == 0:
            QMessageBox.critical(
                self, "Error", "Unable to load the image.", QMessageBox.Ok
            )
            return

        self.scene().clear()
        self.scene().addPixmap(pixmap)
        self.fitInView(self.scene().items()[0], Qt.KeepAspectRatio)
        self.scene().setSceneRect(
            0, 0, pixmap.width(), pixmap.height()
        )
        self.url = file_path
        self.rectangles = []
        self.updated_labels.emit(self.rectangles)

    def mousePressEvent(self, event):
        if event.button() == Qt.LeftButton and self.current_mode == "rect_selection":
            self.start_point = self.mapToScene(event.pos())
            self.drawing = True
        elif event.button() == Qt.MiddleButton:
            self.middle_mouse_button_pressed = True
            self.middle_mouse_last_position = event.pos()

        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            self.draw_rectangle()

        elif self.middle_mouse_button_pressed:
            delta = event.pos() - self.middle_mouse_last_position
            self.middle_mouse_last_position = event.pos()

            value_x = self.horizontalScrollBar().value() - delta.x()
            value_y = self.verticalScrollBar().value() - delta.y()
            self.horizontalScrollBar().setValue(value_x)
            self.verticalScrollBar().setValue(value_y)

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if self.drawing:
            self.end_point = self.mapToScene(event.pos())
            self.draw_rectangle()
            self.drawing = False

            rectangle_item = RectangleItem(self.start_point, self.end_point)
            if rectangle_item.rect().width() < 5 or rectangle_item.rect().height() < 5:
                self.scene().removeItem(rectangle_item)
                self.scene().removeItem(self.rect_item)
                return

            rectangle_item.label_name = self.generate_label_name()
            self.rectangles.append(rectangle_item)
            self.scene().addItem(rectangle_item)
            if self.rect_item in self.scene().items():
                self.scene().removeItem(self.rect_item)

            self.label_added.emit(self.rectangles)

        elif event.button() == Qt.MiddleButton:
            self.middle_mouse_button_pressed = False

        super().mouseReleaseEvent(event)

    def draw_rectangle(self):
        if self.rect_item in self.scene().items():
            self.scene().removeItem(self.rect_item)
        self.rect_item = QGraphicsRectItem()
        pen = QPen(QColor(255, 0, 0))
        pen.setStyle(Qt.DashLine)
        brush = QBrush(QColor(255, 0, 0, 128))
        self.rect_item.setPen(pen)
        self.rect_item.setBrush(brush)

        rect = self.calculate_rectangle()
        self.rect_item.setRect(rect)
        self.scene().addItem(self.rect_item)
        # self.rectangles.append(rect)

    def calculate_rectangle(self):
        x1, y1 = self.start_point.x(), self.start_point.y()
        x2, y2 = self.end_point.x(), self.end_point.y()
        return QRectF(QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2)))

    def set_select_mode(self):
        self.setDragMode(QGraphicsView.RubberBandDrag)
        self.setCursor(Qt.ArrowCursor)
        self.current_mode = "select"

        for rectangle in self.rectangles:
            rectangle.selectable = True
            rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, True)
            rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, True)

    def set_rect_selection(self):
        self.setDragMode(QGraphicsView.NoDrag)
        self.setCursor(Qt.CrossCursor)
        self.current_mode = "rect_selection"

        for rectangle in self.rectangles:
            rectangle.selectable = False
            rectangle.setFlag(QGraphicsRectItem.ItemIsMovable, False)
            rectangle.setFlag(QGraphicsRectItem.ItemIsSelectable, False)

    def generate_label_name(self):
        label_names = [rectangle.label_name for rectangle in self.rectangles]
        i = 0
        while True:
            label_name = f"Label {i}"
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
