import math

from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QObject
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor

from src.utils.functions import calculate_handle_size


class RectangleItem(QGraphicsRectItem):
    start_resizing = Signal()
    stop_resizing = Signal()

    def __init__(
        self,
        parent,
        start_point,
        end_point,
        label_name,
        label_name_id,
        temporary=False,
    ):
        super().__init__()
        self.setRect(self.calculate_rectangle(start_point, end_point))

        self.temporary = temporary
        self.parent = parent

        self.resize_handles = []

        self.default_pen = QPen(QColor(255, 0, 0))
        self.default_brush = QBrush(QColor(255, 0, 0, 32))
        self.default_pen.setWidth(0.1)

        self.start_point = start_point
        self.end_point = end_point

        self.label_name = label_name
        self.label_name_id = label_name_id

        self.min_handle_size = 1
        self.max_handle_size = 40

        self.set_default_color()
        if not self.temporary:
            self.add_resize_handles()
            self.setAcceptHoverEvents(True)

        self.setFlag(QGraphicsRectItem.ItemIsMovable)

    def to_dict(self):
        return {
            "type": "RectangleItem",
            "start_point": [self.start_point.x(), self.start_point.y()],
            "end_point": [self.end_point.x(), self.end_point.y()],
            "label_name": self.label_name,
            "label_name_id": self.label_name_id,
        }

    @classmethod
    def from_dict(cls, data, parent):
        rectangle = cls(
            parent,
            QPointF(*data["start_point"]),
            QPointF(*data["end_point"]),
            data["label_name"],
            data["label_name_id"],
        )
        return rectangle

    @staticmethod
    def calculate_rectangle(start_point, end_point):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()

        return QRectF(
            QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2))
        )

    def update_handle_scale(self, scale_factor):
        """
        Adjust the size of the resize handles based on the scale factor.
        """
        handle_size = calculate_handle_size(
            self.parent.image_width,
            self.parent.image_height,
            scale_factor,
            self.min_handle_size,
            self.max_handle_size,
        )
        for handle in self.resize_handles:
            handle.set_size(handle_size)

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def to_coco_annotation(self):
        # Logic to convert rectangle to COCO annotation
        x, y, w, h = (
            self.rect().x(),
            self.rect().y(),
            self.rect().width(),
            self.rect().height(),
        )
        segmentation = [[x, y, x + w, y, x + w, y + h, x, y + h]]
        return {
            "segmentation": segmentation,
            "category_id": self.label_name_id,
            "bbox": [x, y, w, h],
            "area": w * h,
        }

    def to_yolo_label(self, image_width, image_height):
        # Convert rectangle to YOLO format
        cx = (self.rect().x() + self.rect().width() / 2) / image_width
        cy = (self.rect().y() + self.rect().height() / 2) / image_height
        w = self.rect().width() / image_width
        h = self.rect().height() / image_height
        return f"{self.label_name_id} {cx:.6f} {cy:.6f} {w:.6f} {h:.6f}"

    def mouseMoveEvent(self, event):
        super().mouseMoveEvent(event)

        delta = event.scenePos() - event.lastScenePos()
        self.start_point += delta
        self.end_point += delta
        self.setRect(self.calculate_rectangle(self.start_point, self.end_point))
        self.setPos(0, 0)
        self.update_handlers()
        self.parent.update_labels()

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemSelectedChange:
            if value:
                self.bring_to_front()
            else:
                self.bring_to_back()

        return super().itemChange(change, value)

    def set_hover_color(self):
        hover_brush = QBrush(QColor(255, 0, 0, 64))

        self.setBrush(hover_brush)

    def hoverEnterEvent(self, event):
        self.set_hover_color()

    def hoverLeaveEvent(self, event):
        self.set_default_color()

    def resize_started(self):
        self.parent.movable_disable()
        self.parent.resize_disable()

    def resize_stopped(self):
        self.parent.movable_enable()
        self.parent.resize_enable()
        self.parent.update_labels()

    def add_resize_handles(self):
        handle_size = 5
        half_size = handle_size / 2

        for x, y in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            handle = RectangleHandleItem(
                -half_size, -half_size, handle_size, handle_size, self
            )
            handle.setPos(
                self.rect().x() + x * self.rect().width(),
                self.rect().y() + y * self.rect().height(),
            )
            handle.setBrush(QBrush(QColor(255, 0, 0)))
            handle.setData(0, (x, y))

            self.resize_handles.append(handle)

    def update_handlers(self):
        for handle in self.resize_handles:
            x_offset, y_offset = handle.data(0)

            handle.setPos(
                self.rect().x() + x_offset * self.rect().width(),
                self.rect().y() + y_offset * self.rect().height(),
            )

    def bring_to_front(self):
        self.setZValue(1)
        for handle in self.resize_handles:
            handle.setZValue(1)

    def bring_to_back(self):
        self.setZValue(0)
        for handle in self.resize_handles:
            handle.setZValue(0)


class RectangleHandleItem(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)
        self.parent = parent
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0.5)
        pen.setStyle(Qt.SolidLine)
        self.resizing = False

        self.setPen(pen)

    def mousePressEvent(self, event):
        self.parent.resize_started()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x_offset, y_offset = self.data(0)
        image_width = self.parent.parent.image_width
        image_height = self.parent.parent.image_height
        x, y = (
            event.pos().x() - event.lastPos().x(),
            event.pos().y() - event.lastPos().y(),
        )

        if x_offset == 0:
            new_width = self.parent.rect().width() - x
            new_x = self.parent.rect().x() + (self.parent.rect().width() - new_width)
        else:
            new_width = self.parent.rect().width() + x
            new_x = self.parent.rect().x()

        if y_offset == 0:
            new_height = self.parent.rect().height() - y
            new_y = self.parent.rect().y() + (self.parent.rect().height() - new_height)
        else:
            new_height = self.parent.rect().height() + y
            new_y = self.parent.rect().y()

        x1 = max(0, min(new_x, image_width))
        y1 = max(0, min(new_y, image_height))
        x2 = max(0, min(new_x + new_width, image_width))
        y2 = max(0, min(new_y + new_height, image_height))

        self.parent.start_point = QPointF(x1, y1)
        self.parent.end_point = QPointF(x2, y2)
        self.parent.setRect(
            self.parent.calculate_rectangle(
                self.parent.start_point, self.parent.end_point
            )
        )
        # new_rect = QRectF(new_x, new_y, new_width, new_height)
        # self.parent.setRect(new_rect)
        super().mouseMoveEvent(event)
        self.parent.update_handlers()

    def set_size(self, size):
        """
        Set the size of the handle.
        """
        self.setRect(-size / 2, -size / 2, size, size)

    def mouseReleaseEvent(self, event):
        self.parent.resize_stopped()
        super().mouseReleaseEvent(event)
