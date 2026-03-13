from PyQt6.QtCore import QRectF, Qt, pyqtSignal
from PyQt6.QtGui import QBrush, QColor, QPainter, QWheelEvent
from PyQt6.QtWidgets import QGraphicsView

import theme


class MainPart(QGraphicsView):
    """Canvas widget — dot-grid background, smooth zoom & pan."""

    zoom_changed = pyqtSignal(int)  # emits zoom % as int

    ZOOM_FACTOR = 1.15
    ZOOM_MIN = 0.08
    ZOOM_MAX = 8.0

    def __init__(self, window):
        super().__init__(window.scene)
        self._is_panning = False
        self._pan_start_x = 0.0
        self._pan_start_y = 0.0
        self._zoom_level = 1.0

        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorViewCenter)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setBackgroundBrush(QBrush(QColor(theme.CANVAS_BG)))

        # Hide scrollbars — panning is via mouse drag
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)

        # Large scene rect so the canvas feels "infinite"
        self.setSceneRect(-50000, -50000, 100000, 100000)

    # ── Background ───────────────────────────────────────────────────────────

    def drawBackground(self, painter: QPainter, rect: QRectF):
        super().drawBackground(painter, rect)

        # Dot-grid
        grid = 24
        dot_r = 1.0

        dot_color = QColor(
            theme.CANVAS_DOT if theme.CANVAS_DOT.endswith("98") else theme.CANVAS_DOT
        )
        # Parse the color manually if it has an alpha
        dot_color = QColor(28, 32, 52, 110)

        painter.setPen(Qt.PenStyle.NoPen)
        painter.setBrush(QBrush(dot_color))

        left = int(rect.left()) - (int(rect.left()) % grid) - grid
        top = int(rect.top()) - (int(rect.top()) % grid) - grid
        right = int(rect.right()) + grid
        bottom = int(rect.bottom()) + grid

        for x in range(left, right, grid):
            for y in range(top, bottom, grid):
                painter.drawEllipse(QRectF(x - dot_r, y - dot_r, dot_r * 2, dot_r * 2))

    # ── Zoom ─────────────────────────────────────────────────────────────────

    def zoom_step(self, direction: int):
        """direction: +1 = zoom in, -1 = zoom out."""
        if direction > 0:
            if self._zoom_level >= self.ZOOM_MAX:
                return
            factor = self.ZOOM_FACTOR
            self._zoom_level = min(self._zoom_level * factor, self.ZOOM_MAX)
        else:
            if self._zoom_level <= self.ZOOM_MIN:
                return
            factor = 1.0 / self.ZOOM_FACTOR
            self._zoom_level = max(self._zoom_level * factor, self.ZOOM_MIN)

        self.scale(factor, factor)
        self.zoom_changed.emit(int(self._zoom_level * 100))

    def reset_zoom(self):
        self.resetTransform()
        self._zoom_level = 1.0
        self.zoom_changed.emit(100)

    def fit_view(self):
        items_rect = self.scene().itemsBoundingRect()
        if items_rect.isNull():
            return
        padded = items_rect.adjusted(-80, -80, 80, 80)
        self.fitInView(padded, Qt.AspectRatioMode.KeepAspectRatio)
        sx = self.transform().m11()
        self._zoom_level = sx
        self.zoom_changed.emit(int(sx * 100))

    # ── Events ───────────────────────────────────────────────────────────────

    def wheelEvent(self, event: QWheelEvent):
        if event.modifiers() & Qt.KeyboardModifier.ControlModifier:
            delta = event.angleDelta().y()
            self.zoom_step(+1 if delta > 0 else -1)
        else:
            # Default scroll (no Ctrl) — pan vertically
            dy = event.angleDelta().y()
            dx = event.angleDelta().x()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() - dx // 2)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() - dy // 2)

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        if event.button() == Qt.MouseButton.LeftButton and not [
            obj for obj in self.scene().selectedItems() if not obj.group
        ]:
            self._is_panning = True
            self._pan_start_x = event.position().x()
            self._pan_start_y = event.position().y()
            self.setCursor(Qt.CursorShape.ClosedHandCursor)

    def mouseMoveEvent(self, event):
        if self._is_panning:
            dx = self._pan_start_x - event.position().x()
            dy = self._pan_start_y - event.position().y()
            self._pan_start_x = event.position().x()
            self._pan_start_y = event.position().y()
            self.horizontalScrollBar().setValue(int(self.horizontalScrollBar().value() + dx))
            self.verticalScrollBar().setValue(int(self.verticalScrollBar().value() + dy))
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self._is_panning = False
            self.setCursor(Qt.CursorShape.ArrowCursor)
        super().mouseReleaseEvent(event)
