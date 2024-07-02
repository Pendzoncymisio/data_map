from PyQt5.QtCore import QRectF, QLineF
from PyQt5.QtWidgets import QGraphicsItem

class Line(QGraphicsItem):
    def __init__(self, startSquare, endSquare):
        super().__init__()
        self.setZValue(1)
        self.source_doc = startSquare
        self.sink_doc = endSquare

        self.line = QLineF(startSquare.x, startSquare.y, endSquare.x, endSquare.y)

    def boundingRect(self):
        return QRectF(self.line.p1(), self.line.p2())

    def paint(self, painter, option, widget):
        painter.drawLine(self.line)

    def update_position(self):
        self.prepareGeometryChange()
        self.line = QLineF(self.source_doc.pos(), self.sink_doc.pos())