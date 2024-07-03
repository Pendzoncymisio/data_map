import math

from PyQt5.QtCore import QRectF, QLineF, QPointF
from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtGui import QPolygonF

class Line(QGraphicsItem):
    def __init__(self, startSquare, endSquare):
        super().__init__()
        self.setZValue(1)
        self.source_doc = startSquare
        self.sink_doc = endSquare

        self.line = QLineF(startSquare.pos().x(), startSquare.pos().y(), endSquare.pos().x(), endSquare.pos().y())

    def boundingRect(self):
        return QRectF(self.line.p1(), self.line.p2())

    def paint(self, painter, option, widget):
        painter.drawLine(self.line)
        print("Line", self.line.x1(), self.line.y1(), self.line.x2(), self.line.y2())

        arrow_size = 20.0
        angle = math.atan2(-self.line.dy(), self.line.dx())

        arrow_p1 = self.line.p2() - QPointF(math.sin(angle + math.pi / 3) * arrow_size,
                                             math.cos(angle + math.pi / 3) * arrow_size)
        arrow_p2 = self.line.p2() - QPointF(math.sin(angle + math.pi - math.pi / 3) * arrow_size,
                                             math.cos(angle + math.pi - math.pi / 3) * arrow_size)

        arrow_head = QPolygonF([self.line.p2(), arrow_p1, arrow_p2])
        painter.drawPolygon(arrow_head)

    def update_position(self):
        self.prepareGeometryChange()
        self.line = QLineF(self.source_doc.pos(), self.sink_doc.pos())