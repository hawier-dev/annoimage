from PySide6.QtGui import QPen, QBrush, QColor
from PySide6.QtWidgets import QGraphicsPolygonItem


class PolygonItem(QGraphicsPolygonItem):
    def __init__(
        self, polygon, label_name, label_id, image_width, image_height, parent
    ):
        super().__init__(polygon)
        self.image_view = parent
        self.label_name = label_name
        self.label_coco = None
        self.label_id = label_id
        self.image_width = image_width
        self.image_height = image_height
        self.selectable = True
        self.hovered = False
        self.default_pen = QPen(QColor(0, 255, 0))
        self.default_brush = QBrush(QColor(0, 255, 0, 32))
        self.set_default_color()
        self.setAcceptHoverEvents(True)

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

    def create_yolo_label(self):
        pass

    def set_hover_color(self):
        hover_pen = QPen(QColor(0, 255, 0))
        hover_brush = QBrush(QColor(0, 255, 0, 64))
        self.setPen(hover_pen)
        self.setBrush(hover_brush)

    def hoverEnterEvent(self, event):
        if self.selectable:
            self.set_hover_color()

    def hoverLeaveEvent(self, event):
        if self.selectable:
            self.set_default_color()
