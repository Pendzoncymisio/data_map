from PyQt6.QtWidgets import QGraphicsView, QGraphicsRectItem
from PyQt6.QtCore import Qt


from git import Repo

class MainPart(QGraphicsView):
    def __init__(self, window):
        super().__init__(window.scene)
        self._is_panning = False
        self._pan_start_x = 0
        self._pan_start_y = 0

        window.scene.addItem(QGraphicsRectItem(0, 0, 100, 100))

    def mousePressEvent(self, event):
        super().mousePressEvent(event)
        # Check if the left mouse button is pressed and no final item is selected
        if event.button() == Qt.MouseButton.LeftButton and not [obj for obj in self.scene().selectedItems() if not obj.group]:
            self._is_panning = True
            self._pan_start_x = event.position().x()
            self._pan_start_y = event.position().y()

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
        super().mouseReleaseEvent(event)