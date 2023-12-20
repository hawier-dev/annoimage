from PySide6.QtCore import Qt, QPointF
from PySide6.QtGui import QPen, QBrush, QColor, QPolygonF
from PySide6.QtWidgets import QGraphicsPolygonItem


class PolygonItem(QGraphicsPolygonItem):
    def __init__(self, parent, polygon, label_name, label_name_id):
        super().__init__(polygon)
        self.image_view = parent
        self.label_name = label_name
        self.label_name_id = label_name_id
        self.selectable = True
        self.hovered = False
        self.default_pen = QPen(QColor(255, 0, 0))
        self.default_pen.setStyle(Qt.DashLine)
        self.default_brush = QBrush(QColor(255, 0, 0, 32))
        self.set_default_color()
        self.setAcceptHoverEvents(True)

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

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
        hover_pen = QPen(QColor(255, 0, 0))
        hover_brush = QBrush(QColor(255, 0, 0, 64))
        self.setPen(hover_pen)
        self.setBrush(hover_brush)

    def hoverEnterEvent(self, event):
        if self.selectable:
            self.set_hover_color()

    def hoverLeaveEvent(self, event):
        if self.selectable:
            self.set_default_color()