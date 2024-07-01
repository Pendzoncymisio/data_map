from PyQt5.QtWidgets import QGraphicsItem
from PyQt5.QtCore import Qt, QRectF, QSizeF
from PyQt5.QtGui import QPixmap

import json

from line import Line

class DocsObj(QGraphicsItem):
    def __init__(self, id, payload):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.id = id
        self.payload = payload

        self.icon = payload.get("icon", "default_icon.png")
        self.x = payload.get("x", 0)
        self.y = payload.get("y", 0)
        self.w = 100
        self.h = 100

        self.outbound_lines = []
        self.inbound_lines = []

        self.parent_doc = None
        self.children_docs = []

    def itemChange(self, change, value):
        result = super().itemChange(change, value)
        if change == QGraphicsItem.ItemPositionChange:
            self.x = value.x()
            self.y = value.y()
            for line in self.outbound_lines + self.inbound_lines:
                line.update_position()
            if self.parent_doc:
                self.parent_doc.__update_position()

        elif change == QGraphicsItem.ItemSelectedChange:
            if value:
                print("Square selected!", self.id)
                self.__select_square()
            else:
                print("Square deselected!")
                self.__deselect_square()
        
        return result
    
    def add_child_document(self, node):
        """
        Add a child node to the DocsObj.

        Args:
            node (DocsObj): The child node to be added.
        """
        self.children_docs.append(node)

    def remove_child_document(self, node):
        """
        Remove a child node from the DocsObj.

        Args:
            node (DocsObj): The child node to be removed.
        """
        self.children_docs.remove(node)

    def make_group(self):
        """
        Make the DocsObj a group.
        """
        self.group = True

        self.setZValue(0)
    
    def make_final(self):
        """
        Make the DocsObj a final node.
        """
        self.group = False

        self.setZValue(2)
        #self.setPos(QPointF(x, y))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def paint(self, painter, option, widget):
        if self.group:
            painter.drawRect(self.boundingRect())
            icon_size = QSizeF(QPixmap(self.icon).size())
            icon_rect = QRectF(self.boundingRect().topRight(), icon_size)
            painter.drawPixmap(icon_rect, QPixmap(self.icon), QRectF(QPixmap(self.icon).rect()))
            return
        pixmap = QPixmap(self.icon)
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(pixmap.rect()))
        painter.drawText(QRectF(0, 50, 50, 20), Qt.AlignCenter, str(self.id))

    def boundingRect(self):
        if self.group:
            return QRectF(self.x, self.y, self.w, self.h)
        return QRectF(0, 0, 50, 50) #QRectF(self.x, self.y, self.w, self.h)
    
    def get_sources(self):
        return [line.source_doc for line in self.inbound_lines]
    
    def add_source(self, source):
        self.sources.append(Line(source, self))
    
    def get_sinks(self):
        return [line.sink_doc for line in self.outbound_lines]
    
    def add_sink(self, sink):
        self.outbound_lines.append(Line(self, sink))
    
    def __select_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        window.sidebar.text_area.setText(json.dumps(self.payload))
    
    def __deselect_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        text = window.sidebar.text_area.toPlainText()
        if text:
            window.sidebar.text_area.clear()
            #TODO: Think if that should be done as doc_ref.update_payload(payload)
            self.payload = json.loads(text)
            self.__update_viz()
        else:
            print("No text in the text area - if you want to delete the node, press the delete button.")
    
    def __update_position(self):
        self.prepareGeometryChange()
        self.rectangle = self.__recalculate_rect()
        print([(children.x, children.y) for children in self.children_docs])

    def __update_viz(self):
        #TODO: Everything in viz should update, and icon should be on viz level
        self.icon = self.payload["icon"]   

    def __recalculate_rect(self):
        if not self.children_docs:
            return QRectF(0, 0, 0, 0)
        min_x = min(child.x for child in self.children_docs)
        min_y = min(child.y for child in self.children_docs)
        max_x = max(child.x + child.w for child in self.children_docs)
        max_y = max(child.y + child.h for child in self.children_docs)

        self.x = min_x
        self.y = min_y
        self.w = max_x - min_x
        self.h = max_y - min_y

        return QRectF(self.x, self.y, self.w, self.h)