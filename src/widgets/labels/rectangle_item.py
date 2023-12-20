from PySide6.QtCore import Qt, QPointF, QRectF, Signal, QObject
from PySide6.QtWidgets import QGraphicsRectItem, QGraphicsEllipseItem, QGraphicsItem
from PySide6.QtGui import QPen, QBrush, QColor


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
        self.default_pen.setStyle(Qt.DashLine)
        self.default_brush = QBrush(QColor(255, 0, 0, 32))

        self.start_point = start_point
        self.end_point = end_point

        self.selectable = True
        self.hovered = False
        self.label_name = label_name
        self.label_name_id = label_name_id

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

    def set_default_color(self):
        if self.temporary:
            self.setPen(QPen(QColor(255, 0, 0)))
            self.setBrush(QBrush(QColor(255, 0, 0, 32)))
        else:
            self.setPen(self.default_pen)
            self.setBrush(self.default_brush)

    # def create_yolo_label(self):
    #     x = (self.rect().x() + self.rect().width() / 2) / self.image_width
    #     y = (self.rect().y() + self.rect().height() / 2) / self.image_height
    #     width = self.rect().width() / self.image_width
    #     height = self.rect().height() / self.image_height
    #
    #     label_string = f"{self.label_name_id} {x:.6f} {y:.6f} {width:.6f} {height:.6f}"
    #     return label_string

    # def create_coco_label(self):
    #     json_dict = {
    #         "category_id": self.label_name_id,
    #         "segmentation": [
    #             [
    #                 self.rect().x(),
    #                 self.rect().y(),
    #                 self.rect().x() + self.rect().width(),
    #                 self.rect().y() + self.rect().height(),
    #             ]
    #         ],
    #         "area": self.rect().width() * self.rect().height(),
    #         "bbox": [
    #             self.rect().x(),
    #             self.rect().y(),
    #             self.rect().width(),
    #             self.rect().height(),
    #         ],
    #         "iscrowd": 0,
    #     }
    #
    #     return json_dict

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

    def resize_started(self):
        self.parent.movable_disable()

    def resize_stopped(self):
        self.parent.movable_enable()

    def add_resize_handles(self):
        handle_size = 5
        half_size = handle_size / 2

        for x, y in [(0, 0), (1, 0), (0, 1), (1, 1)]:
            handle = HandleItem(-half_size, -half_size, handle_size, handle_size, self)
            handle.setPos(
                self.rect().x() + x * self.rect().width(),
                self.rect().y() + y * self.rect().height(),
            )
            handle.setFlag(QGraphicsEllipseItem.ItemIsMovable)
            handle.setBrush(QBrush(QColor(255, 0, 0)))
            handle.setData(0, (x, y))

            self.resize_handles.append(handle)

    def update_handlers(self):
        for handle in self.resize_handles:
            x_offset, y_offset = handle.data(0)
            handle_size = min(self.rect().width(), self.rect().height()) * 0.05

            handle.setRect(
                -handle_size / 2,
                -handle_size / 2,
                handle_size,
                handle_size,
            )
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


class HandleItem(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent):
        super().__init__(x, y, w, h, parent)
        self.parent = parent
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0.5)
        pen.setStyle(Qt.SolidLine)

        self.setPen(pen)

    def mousePressEvent(self, event):
        self.parent.resize_started()
        super().mousePressEvent(event)

    def mouseMoveEvent(self, event):
        x_offset, y_offset = self.data(0)
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

        x1 = max(0, min(new_x, self.parent.image_width))
        y1 = max(0, min(new_y, self.parent.image_height))
        x2 = max(0, min(new_x + new_width, self.parent.image_width))
        y2 = max(0, min(new_y + new_height, self.parent.image_height))

        self.parent.start_point = QPointF(x1, y1)
        self.parent.end_point = QPointF(x2, y2)
        self.parent.setRect(
            self.parent.calculateRectangle(
                self.parent.start_point, self.parent.end_point
            )
        )
        # new_rect = QRectF(new_x, new_y, new_width, new_height)
        # self.parent.setRect(new_rect)
        super().mouseMoveEvent(event)
        self.parent.update_handlers()

    def mouseReleaseEvent(self, event):
        self.parent.resize_stopped()
        super().mouseReleaseEvent(event)