from PySide6.QtCore import Qt, QPointF, QRectF, Signal
from PySide6.QtWidgets import QGraphicsRectItem
from PySide6.QtGui import QPen, QBrush, QColor


class RectangleItem(QGraphicsRectItem):
    def __init__(self, start_point, end_point):
        super().__init__()
        self.setRect(self.calculateRectangle(start_point, end_point))

        self.default_pen = QPen(QColor(200, 0, 0))
        self.default_pen.setStyle(Qt.DashLine)
        self.default_brush = QBrush(QColor(200, 0, 0, 64))

        self.selectable = True
        self.hovered = False
        self.label_name = None

        self.set_default_color()
        self.setAcceptHoverEvents(True)

        self.resizable = True

    @staticmethod
    def calculateRectangle(start_point, end_point):
        x1, y1 = start_point.x(), start_point.y()
        x2, y2 = end_point.x(), end_point.y()
        return QRectF(QPointF(min(x1, x2), min(y1, y2)), QPointF(max(x1, x2), max(y1, y2)))

    def set_default_color(self):
        self.setPen(self.default_pen)
        self.setBrush(self.default_brush)

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
