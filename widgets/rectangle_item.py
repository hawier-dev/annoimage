from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtGui import QPen, QBrush, QColor


class RectangleItem(QGraphicsRectItem):
    def __init__(
        self, start_point, end_point, label_name, label_id, image_width, image_height
    ):
        super().__init__()
        self.setRect(self.calculateRectangle(start_point, end_point))

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
