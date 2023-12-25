from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF
from PySide6.QtWidgets import QGraphicsPolygonItem, QGraphicsEllipseItem

from src.utils.functions import calculate_handle_size
from src.widgets.labels.rectangle_item import RectangleItem


class PolygonItem(QGraphicsPolygonItem):
    def __init__(self, parent, polygon, label_name, label_name_id):
        super().__init__(polygon)
        self.parent = parent
        self.label_name = label_name
        self.label_name_id = label_name_id
        self.selectable = True
        self.hovered = False
        self.resize_handles = []
        self.min_handle_size = 0.01
        self.max_handle_size = 40

        self.default_pen = QPen(QColor(255, 0, 0))
        self.default_pen.setWidth(0.1)
        self.default_brush = QBrush(QColor(255, 0, 0, 32))
        self.set_default_color()
        self.setAcceptHoverEvents(True)

        self.add_resize_handles()

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def to_coco_annotation(self):
        segmentation = [[point.x(), point.y()] for point in self.polygon()]

        bbox = self.get_bounding_box()

        return {
            "segmentation": [segmentation],
            "bbox": [bbox.x(), bbox.y(), bbox.width(), bbox.height()],
            "area": bbox.width() * bbox.height(),
            "category_id": self.label_name_id,
            "iscrowd": 0,
        }

    def update_handle_scale(self, scale_factor):
        """
        Adjust the size of the resize handles based on the scale factor.
        """
        handle_size = calculate_handle_size(
            self.parent.image_width, self.parent.image_height, scale_factor, self.min_handle_size, self.max_handle_size
        )
        for handle in self.resize_handles:
            handle.set_size(handle_size)

    def get_bounding_box(self):
        return self.polygon().boundingRect()

    def to_rectangle_item(self):
        """
        Converts current object to a RectangleItem.
        Returns:
            RectangleItem: The converted RectangleItem object.
        """
        bbox = self.get_bounding_box()
        return RectangleItem(
            self.parent,
            bbox.topLeft(),
            bbox.bottomRight(),
            self.label_name,
            self.label_name_id,
        )

    def to_dict(self):
        return {
            "type": "PolygonItem",
            "polygon": [list(point.toTuple()) for point in self.polygon()],
            "label_name": self.label_name,
            "label_name_id": self.label_name_id,
        }

    @classmethod
    def from_dict(cls, data, parent):
        points = [QPointF(point[0], point[1]) for point in data["polygon"]]
        polygon = QPolygonF(points)
        return cls(parent, polygon, data["label_name"], data["label_name_id"])

    def set_hover_color(self):
        hover_brush = QBrush(QColor(255, 0, 0, 64))
        self.setBrush(hover_brush)

    def hoverEnterEvent(self, event):
        self.set_hover_color()

    def hoverLeaveEvent(self, event):
        self.set_default_color()

    def add_resize_handles(self):
        for i, point in enumerate(self.polygon()):
            handle = PolygonHandleItem(-2.5, -2.5, 5, 5, self, i)
            handle.setPos(point)
            self.resize_handles.append(handle)

    def move_vertex(self, index, new_pos):
        old_polygon = self.polygon()
        points = [old_polygon[i] for i in range(old_polygon.count())]

        points[index] = new_pos

        new_polygon = QPolygonF(points)
        self.setPolygon(new_polygon)


class PolygonHandleItem(QGraphicsEllipseItem):
    def __init__(self, x, y, w, h, parent, index):
        super().__init__(x, y, w, h, parent)
        self.parent = parent
        self.index = index  # Index of the vertex in the polygon
        self.setFlag(QGraphicsEllipseItem.ItemIsMovable)
        self.setBrush(QBrush(QColor(255, 0, 0)))
        pen = QPen(QColor(0, 0, 0))
        pen.setWidth(0.5)
        pen.setStyle(Qt.SolidLine)

        self.setPen(pen)

    def mouseMoveEvent(self, event):
        QGraphicsEllipseItem.mouseMoveEvent(self, event)
        new_pos = self.pos() + event.pos() - event.lastPos()
        self.parent.move_vertex(self.index, new_pos)

    def set_size(self, size):
        """
        Set the size of the handle.
        """
        self.setRect(-size / 2, -size / 2, size, size)
