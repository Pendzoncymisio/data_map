import math

from PyQt6.QtCore import QPointF, QRectF, Qt
from PyQt6.QtGui import QBrush, QColor, QPainter, QPainterPath, QPen, QPolygonF
from PyQt6.QtWidgets import QGraphicsItem

import theme

# Should match CARD_SIZE in doc_obj.py
_CARD_SIZE = 80


class Line(QGraphicsItem):
    """Bezier connection line with a filled arrowhead."""

    def __init__(self, startSquare, endSquare):
        super().__init__()
        self.setZValue(1)
        self.source_doc = startSquare
        self.sink_doc = endSquare
        self._path = QPainterPath()
        self._p1 = QPointF()
        self._p2 = QPointF()
        self.update_position()

    # ── Geometry ─────────────────────────────────────────────────

    def _connector_points(self):
        """Return (start_point, end_point) at the closest edges of the two nodes."""
        src = self.source_doc
        snk = self.sink_doc
        src_cx = src.pos().x() + _CARD_SIZE / 2
        src_cy = src.pos().y() + _CARD_SIZE / 2
        snk_cx = snk.pos().x() + _CARD_SIZE / 2
        snk_cy = snk.pos().y() + _CARD_SIZE / 2

        dx = snk_cx - src_cx
        dy = snk_cy - src_cy

        if abs(dx) >= abs(dy):
            if dx >= 0:
                p1 = QPointF(src.pos().x() + _CARD_SIZE, src_cy)
                p2 = QPointF(snk.pos().x(), snk_cy)
            else:
                p1 = QPointF(src.pos().x(), src_cy)
                p2 = QPointF(snk.pos().x() + _CARD_SIZE, snk_cy)
        else:
            if dy >= 0:
                p1 = QPointF(src_cx, src.pos().y() + _CARD_SIZE)
                p2 = QPointF(snk_cx, snk.pos().y())
            else:
                p1 = QPointF(src_cx, src.pos().y())
                p2 = QPointF(snk_cx, snk.pos().y() + _CARD_SIZE)

        return p1, p2

    def _build_path(self, p1: QPointF, p2: QPointF) -> QPainterPath:
        """Build a smooth cubic bezier from p1 to p2."""
        path = QPainterPath(p1)
        dx = abs(p2.x() - p1.x())
        dy = abs(p2.y() - p1.y())
        ctrl_dist = max(min(dx, dy) * 0.6, 60.0)

        if abs(p2.x() - p1.x()) >= abs(p2.y() - p1.y()):
            # Horizontal dominant
            cp1 = QPointF(p1.x() + math.copysign(ctrl_dist, p2.x() - p1.x()), p1.y())
            cp2 = QPointF(p2.x() - math.copysign(ctrl_dist, p2.x() - p1.x()), p2.y())
        else:
            # Vertical dominant
            cp1 = QPointF(p1.x(), p1.y() + math.copysign(ctrl_dist, p2.y() - p1.y()))
            cp2 = QPointF(p2.x(), p2.y() - math.copysign(ctrl_dist, p2.y() - p1.y()))

        path.cubicTo(cp1, cp2, p2)
        return path

    def update_position(self):
        self.prepareGeometryChange()
        p1, p2 = self._connector_points()
        self._p1 = p1
        self._p2 = p2
        self._path = self._build_path(p1, p2)

    def boundingRect(self) -> QRectF:
        pad = 20
        return self._path.boundingRect().adjusted(-pad, -pad, pad, pad)

    # ── Painting ─────────────────────────────────────────────────

    def paint(self, painter: QPainter, option, widget):
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)

        # Curved line
        line_pen = QPen(QColor(theme.LINE_COLOR), 1.8)
        line_pen.setStyle(Qt.PenStyle.SolidLine)
        line_pen.setCapStyle(Qt.PenCapStyle.RoundCap)
        line_pen.setJoinStyle(Qt.PenJoinStyle.RoundJoin)
        painter.setPen(line_pen)
        painter.setBrush(Qt.BrushStyle.NoBrush)
        painter.drawPath(self._path)

        # Arrowhead at p2
        self._draw_arrowhead(painter, self._p2)

    def _draw_arrowhead(self, painter: QPainter, tip: QPointF):
        """Draw a filled triangle arrowhead pointing toward `tip`."""
        t_pt = self._path.pointAtPercent(0.95)
        dx = tip.x() - t_pt.x()
        dy = tip.y() - t_pt.y()
        angle = math.atan2(dy, dx)

        size = 11.0
        spread = math.pi / 6  # 30°

        p_left = QPointF(
            tip.x() - size * math.cos(angle - spread), tip.y() - size * math.sin(angle - spread)
        )
        p_right = QPointF(
            tip.x() - size * math.cos(angle + spread), tip.y() - size * math.sin(angle + spread)
        )

        arrow = QPolygonF([tip, p_left, p_right])
        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(QColor(theme.LINE_ARROW)))
        painter.drawPolygon(arrow)
