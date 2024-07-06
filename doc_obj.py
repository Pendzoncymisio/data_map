from PyQt5.QtWidgets import QGraphicsItem, QGraphicsSceneMouseEvent
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QMenu

import json

from line import Line

class DocObj(QGraphicsItem):
    def __init__(self, id, payload, docs_obj_dict):
        super().__init__()
        self.setFlag(QGraphicsItem.ItemSendsGeometryChanges)

        self.id = id
        self.payload = payload

        self.docs_obj_dict = docs_obj_dict # Store reference to the dictionary of all DocObj objects
        docs_obj_dict[id] = self # Object itself is responsible to add itself to the dictionary

        self.icon = payload.get("icon", "default_icon.png")
        viz = payload.get("viz", {"x": 0, "y": 0})
        self.x = 0 # Will be populated after all objects are created
        self.y = 0
        self.rel_x = viz["x"]
        self.rel_y = viz["y"]
        self.w = 100
        self.h = 100
        self.group = False

        self.outbound_lines = []
        self.inbound_lines = []

        self.parent_doc = None
        self.children_docs = []


    def __update_viz(self):
        #TODO: Everything in viz should update, and icon should be on viz level
        self.icon = self.payload.get("icon", "default_icon.png")  

    def itemChange(self, change, value):
        if change == QGraphicsItem.ItemPositionChange:
            #print(self.x, self.y, self.rel_x, self.rel_y, self.pos().x())
            grid_size = 20
            new_pos = value #TODO: Make this a setting, return value if not snapping
            new_pos.setX(round(new_pos.x() / grid_size) * grid_size)
            new_pos.setY(round(new_pos.y() / grid_size) * grid_size)

            for line in self.outbound_lines + self.inbound_lines:
                line.update_position()
            if self.parent_doc:
                self.parent_doc.parent_update_position()
            return new_pos

        elif change == QGraphicsItem.ItemSelectedChange:
            if value:
                print("Square selected!", self.id)
                self.__select_square()
            else:
                print("Square deselected!")
                self.__deselect_square()
            return value
        
        return super().itemChange(change, value)
    
    def update_position(self):
        margin = 20
        text_size = 20 #TODO: Make this a setting
        min_x = min(child.pos().x() for child in self.children_docs)
        min_y = min(child.pos().y() for child in self.children_docs)
        max_x = max(child.pos().x() + child.boundingRect().width() for child in self.children_docs)
        max_y = max(child.pos().y() + child.boundingRect().height() for child in self.children_docs) + text_size

        self.setPos(min_x - margin, min_y - margin)
        self.w = max_x - min_x + 2 * margin
        self.h = max_y - min_y + 2 * margin

        self.update()

    def parent_update_position(self):
        self.update_position()
        if self.parent_doc:
            self.parent_doc.parent_update_position()
    
    def paint(self, painter, option, widget):
        if self.group:
            rect = self.boundingRect()
            painter.setPen(Qt.black)
            #painter.setBrush(Qt.white)
            painter.drawRoundedRect(rect, 10, 10)
            
            icon_size = QSizeF(QPixmap(self.icon).size())
            icon_rect = QRectF(rect.topRight(), icon_size)
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
            return QRectF(0,0, self.w, self.h)
        return QRectF(0, 0, 50, 50)
    
    def add_child_document(self, node):
        """
        Add a child node to the DocObj.

        Args:
            node (DocObj): The child node to be added.
        """
        self.children_docs.append(node)

    def remove_child_document(self, node):
        """
        Remove a child node from the DocObj.

        Args:
            node (DocObj): The child node to be removed.
        """
        self.children_docs.remove(node)

    def make_group(self):
        """
        Make the DocObj a group.
        """
        self.group = True

        self.setZValue(0)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
    
    def make_final(self):
        """
        Make the DocObj a final node.
        """
        self.group = False

        self.setZValue(2)
        #self.setPos(QPointF(x, y))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)

    def create_new_source(self):
        new_obj = DocObj("new", {"icon": "default_icon.png", "viz": {"x": self.pos().x(), "y": self.pos().y() - 100}}, self.docs_obj_dict)
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() - 100)
        line = Line(new_obj, self)
        new_obj.outbound_lines.append(line)
        self.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
        return new_obj
    
    def create_new_sink(self):
        new_obj = DocObj("new", {"icon": "default_icon.png", "sources":[self.id], "viz": {"x": self.pos().x(), "y": self.pos().y() + 100}}, self.docs_obj_dict)
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() + 100)
        line = Line(self, new_obj)
        self.outbound_lines.append(line)
        new_obj.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
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
            x = self.rel_x + self.parent_doc.pos().x()
            y = self.rel_y + self.parent_doc.pos().y()
            self.setPos(x, y)
            print(self.id, x, y, self.rel_x, self.rel_y, self.parent_doc.x, self.parent_doc.y)

    def tree_position_update(self):
        for child in self.children_docs:
            child.calculate_position()
            child.tree_position_update()

    def get_rel_pos(self):
        if self.parent_doc:
            """There is a situation where this might be useful
            rel_x = self.pos().x() - self.parent_doc.pos().x()
            rel_y = self.pos().y() - self.parent_doc.pos().y()"""
            if self.group:
                return {"x": self.x - self.parent_doc.x, "y": self.y - self.parent_doc.y}
            else:
                return {"x": self.pos().x() - self.parent_doc.x, "y": self.pos().y() - self.parent_doc.y}
        else:
            return {"x": self.pos().x(), "y": self.pos().y()}
    
    def __select_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        window.sidebar.text_area.setText(json.dumps(self.payload, indent=2))
        window.sidebar.id_line.setText(self.id)
    
    def __deselect_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        text = window.sidebar.text_area.toPlainText()
        if text:
            window.sidebar.text_area.clear()
            #TODO: Think if that should be done as doc_ref.update_payload(payload)
            try:
                self.payload = json.loads(text)
            except json.JSONDecodeError:
                print("Invalid JSON, try again it.")
            # TODO: Handle changing of the ID
            window.sidebar.id_line.clear()
            self.__update_viz()
        else:
            print("No text in the text area - if you want to delete the node, press the delete button.")
    
    def collapse(self):
        """
        Collapse the group, hiding all child objects and making the group behave as a final object.
        """
        # Hide all child objects
        for child in self.children_docs:
            child.collapse()
            child.setVisible(False)
            for line in child.outbound_lines + child.inbound_lines:
                line.setVisible(False)
                #TODO: Switch them over to group rather than setting invisible

        # Make the group behave as a final object
        self.make_final()
        self.expandable = True

    def expand(self):
        """
        Expand the group, showing all child objects and making the group behave as a group again.
        """
        if not self.expandable:
            print("Nothing to expand!")
            return
        # Show all child objects
        for child in self.children_docs:
            child.setVisible(True)
        for line in child.outbound_lines + child.inbound_lines:
                line.setVisible(True)

        # Make the object behave as a group again
        self.make_group()
        self.parent_update_position()

    def contextMenuEvent(self, event):
        """
        Show a context menu when the user right-clicks on the object.
        """
        context_menu = QMenu()

        # Add actions to the context menu
        expand_action = context_menu.addAction("Expand")
        collapse_action = context_menu.addAction("Collapse")
        add_source_action = context_menu.addAction("Add Source")
        add_sink_action = context_menu.addAction("Add Sink")

        # Show the context menu at the current mouse position
        action = context_menu.exec_(event.screenPos())

        # Handle the selected action
        if action == expand_action:
            self.expand()
        elif action == collapse_action:
            self.collapse()
        elif action == add_source_action:
            self.create_new_source()
        elif action == add_sink_action:
            self.create_new_sink()
        