from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem
from PySide6.QtGui import QPen, QBrush, QColor


class RectangleItem(QGraphicsRectItem):
    start_resizing = Signal()
    stop_resizing = Signal()

    def __init__(
        self, start_point, end_point, label_name, label_id, image_width, image_height,
            parent
    ):
        super().__init__()
        print("RectangleItem init")
        self.setRect(self.calculateRectangle(start_point, end_point))
        self.image_view = parent
        self.resize_handles = []

        self.default_pen = QPen(QColor(255, 0, 0))
        self.default_pen.setStyle(Qt.DashLine)
        self.default_brush = QBrush(QColor(255, 0, 0, 32))

        self.selectable = True
        self.hovered = False
        self.image_width = image_width
        self.image_height = image_height
        self.label_name = label_name
        self.label_type = "YOLO"
        self.label_id = label_id
        self.label_line = self.create_yolo_label()

        self.add_resize_handles()
        self.set_default_color()
        self.setAcceptHoverEvents(True)

    @staticmethod
    def calculateRectangle(start_point, end_point):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()
        return QRectF(
            QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2))
        )

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def create_yolo_label(self):
        x = (self.rect().x() + self.rect().width() / 2) / self.image_width
        y = (self.rect().y() + self.rect().height() / 2) / self.image_height
        width = self.rect().width() / self.image_width
        height = self.rect().height() / self.image_height

        label_string = f"{self.label_id} {x:.6f} {y:.6f} {width:.6f} {height:.6f}"
        return label_string

    def set_hover_color(self):
        hover_pen = QPen(QColor(255, 0, 0))
        hover_pen.setStyle(Qt.DashLine)
        hover_brush = QBrush(QColor(255, 0, 0, 64))

        self.setPen(hover_pen)
        self.setBrush(hover_brush)

    def hoverEnterEvent(self, event):
        if self.selectable:
            self.set_hover_color()

    def hoverLeaveEvent(self, event):
        if self.selectable:
            self.set_default_color()

    def add_resize_handles(self):
        handle_size = min(self.rect().width(), self.rect().height()) * 0.05
        half_size = handle_size / 2

        for x, y in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            handle = HandleItem(-half_size, -half_size, handle_size, handle_size, self)
            handle.setPos(self.rect().x() + x * self.rect().width(), self.rect().y() + y * self.rect().height())
            handle.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            handle.setBrush(QBrush(QColor(255, 0, 0)))
            handle.setData(0, (x, y))

            self.resize_handles.append(handle)

    def update_handlers_position(self):
        for handle in self.resize_handles:
            x_offset, y_offset = handle.data(0)
            handle.setPos(self.rect().x() + x_offset * self.rect().width(), self.rect().y() + y_offset * self.rect().height())


class HandleItem(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)

    def mouseMoveEvent(self, event):
        parent = self.parentItem()
        parent.image_view.movable_disable()
        x_offset, y_offset = self.data(0)
        x, y = event.pos().x() - event.lastPos().x(), event.pos().y() - event.lastPos().y()

        if x_offset == 0:
            new_width = parent.rect().width() - x
            new_x = parent.rect().x() + (parent.rect().width() - new_width)
        else:
            new_width = parent.rect().width() + x
            new_x = parent.rect().x()

        if y_offset == 0:
            new_height = parent.rect().height() - y
            new_y = parent.rect().y() + (parent.rect().height() - new_height)
        else:
            new_height = parent.rect().height() + y
            new_y = parent.rect().y()

        new_rect = QRectF(new_x, new_y, new_width, new_height)
        parent.setRect(new_rect)
        parent.label_line = parent.create_yolo_label()
        parent.update_handlers_position()
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        parent = self.parentItem()
        parent.image_view.movable_enable()
        super().mouseReleaseEvent(event)
