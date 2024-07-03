from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF
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
        viz = payload.get("viz", {"x": 0, "y": 0})
        self.x = 0 # Will be populated after all objects are created
        self.y = 0
        self.rel_x = viz["x"]
        self.rel_y = viz["y"]
        self.w = 100
        self.h = 100

        self.outbound_lines = []
        self.inbound_lines = []

        self.parent_doc = None
        self.children_docs = []

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            #print(self.x, self.y, self.rel_x, self.rel_y, self.pos().x())
            for line in self.outbound_lines + self.inbound_lines:
                line.update_position()
            if self.parent_doc:
                self.parent_doc.__update_position()
            return value

        elif change == QGraphicsItem.ItemSelectedChange:
            if value:
                print("Square selected!", self.id)
                self.__select_square()
            else:
                print("Square deselected!")
                self.__deselect_square()
            return value
        
        return super().itemChange(change, value)
    
    def paint(self, painter, option, widget):
        if self.group:
            painter.drawRect(self.boundingRect())
            icon_size = QSizeF(QPixmap(self.icon).size())
            icon_rect = QRectF(self.boundingRect().topRight(), icon_size)
            painter.drawPixmap(icon_rect, QPixmap(self.icon), QRectF(QPixmap(self.icon).rect()))
            return
        
        pixmap = QPixmap(self.icon)
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(pixmap.rect()))

        # Calculate the width of the text
        text_width = painter.fontMetrics().width(str(self.id))

        # Calculate the position to display the text
        text_x = self.boundingRect().center().x() - text_width / 2
        text_y = self.boundingRect().bottom() + 10

        # Draw the text
        painter.drawText(QRectF(text_x, text_y, text_width, 20), Qt.AlignCenter, str(self.id))

    def boundingRect(self):
        if self.group:
            return QRectF(self.x, self.y, self.w, self.h)
        return QRectF(0, 0, 50, 50)
    
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

        self.setFlag(QGraphicsItem.ItemIsSelectable)
    
    def make_final(self):
        """
        Make the DocsObj a final node.
        """
        self.group = False

        self.setZValue(2)
        #self.setPos(QPointF(x, y))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def create_new_source(self):
        new_obj = DocsObj("new", {"icon": "default_icon.png", "viz": {"x": self.pos().x(), "y": self.pos().y() - 100}})
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() - 100)
        line = Line(new_obj, self)
        new_obj.outbound_lines.append(line)
        self.inbound_lines.append(line)
        return new_obj
    
    def create_new_sink(self):
        new_obj = DocsObj("new", {"icon": "default_icon.png", "sources":[self.id], "viz": {"x": self.pos().x(), "y": self.pos().y() + 100}})
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() + 100)
        line = Line(self, new_obj)
        self.outbound_lines.append(line)
        new_obj.inbound_lines.append(line)
        return new_obj
    
    def get_sources(self):
        return [line.source_doc for line in self.inbound_lines]
    
    #def add_source(self, source):
    #    self.sources.append(Line(source, self))
    
    def get_sinks(self):
        return [line.sink_doc for line in self.outbound_lines]
    
    #def add_sink(self, sink):
    #    self.outbound_lines.append(Line(self, sink))

    def calculate_position(self):
        if self.parent_doc:
            x = self.rel_x + self.parent_doc.x
            y = self.rel_y + self.parent_doc.y
            print(x, y)
            self.setPos(x, y)

    def tree_position_update(self):
        for child in self.children_docs:
            child.calculate_position()
            child.tree_position_update()

    def get_rel_pos(self):
        if self.parent_doc:
            rel_x = self.pos().x() - self.parent_doc.pos().x()
            rel_y = self.pos().y() - self.parent_doc.pos().y()
            return {"x": rel_x, "y": rel_y}
        else:
            return {"x": self.pos().x(), "y": self.pos().y()}
    
    def __select_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        window.sidebar.text_area.setText(json.dumps(self.payload))
        window.sidebar.id_line.setText(self.id)
    
    def __deselect_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        text = window.sidebar.text_area.toPlainText()
        if text:
            window.sidebar.text_area.clear()
            #TODO: Think if that should be done as doc_ref.update_payload(payload)
            self.payload = json.loads(text)
            # TODO: Handle changing of the ID
            window.sidebar.id_line.clear()
            self.__update_viz()
        else:
            print("No text in the text area - if you want to delete the node, press the delete button.")
    
    def __update_position(self):
        self.prepareGeometryChange()
        self.rectangle = self.recalculate_rect()
        #print([(children.x, children.y) for children in self.children_docs])

    def __update_viz(self):
        #TODO: Everything in viz should update, and icon should be on viz level
        self.icon = self.payload.get("icon", "default_icon.png")  

    def recalculate_rect(self):
        if not self.children_docs:
            return QRectF(0, 0, 0, 0)
        min_x = min(child.pos().x() for child in self.children_docs)
        min_y = min(child.pos().y() for child in self.children_docs)
        max_x = max(child.pos().x() + child.w for child in self.children_docs)
        max_y = max(child.pos().y() + child.h for child in self.children_docs)

        self.x = min_x
        self.y = min_y
        self.w = max_x - min_x
        self.h = max_y - min_y

        return QRectF(self.x, self.y, self.w, self.h)