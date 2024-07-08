import os
import json

from PyQt5.QtWidgets import QGraphicsItem, QFileDialog
from PyQt5.QtCore import Qt, QRectF, QSizeF, QPointF
from PyQt5.QtGui import QPixmap, QIcon

from line import Line
from context_menu import ContextMenu

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
        self.expandable = False

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
                self.parent_doc.propagate_postion_up()
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
    
    def update_parent_position(self):
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

    def propagate_postion_up(self, include_self=True):
        if include_self:
            self.update_parent_position()
        if self.parent_doc:
            self.parent_doc.propagate_postion_up()

    def update_child_position(self, z_value):
        self.setZValue(z_value)
        rel_pos = self.get_rel_pos()
        self.rel_x = rel_pos["x"]
        self.rel_y = rel_pos["y"]
        if self.parent_doc:
            x = self.rel_x + self.parent_doc.pos().x()
            y = self.rel_y + self.parent_doc.pos().y()
            self.setPos(x, y)
            #print(self.id, x, y, self.rel_x, self.rel_y, self.parent_doc.x, self.parent_doc.y)
        
        self.update()

    def propagate_postion_down(self, z_value=0):
        for child in self.children_docs:
            child.update_child_position(z_value + 1)
            child.propagate_postion_down(z_value + 1)

    def get_rel_pos(self):
        if self.parent_doc:
            rel_x = self.pos().x() - self.parent_doc.pos().x()
            rel_y = self.pos().y() - self.parent_doc.pos().y()
            return {"x": rel_x, "y": rel_y}
        else:
            return {"x": self.pos().x(), "y": self.pos().y()}
    
    def paint(self, painter, option, widget):
        if self.group:
            rect = self.boundingRect()
            painter.setPen(Qt.black)
            # painter.setBrush(Qt.white)
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
        #text_x = self.boundingRect().center().x() - text_width / 2
        text_width = 120
        text_x = self.boundingRect().center().x() - text_width / 2
        text_y = self.boundingRect().bottom() + 10

        # Wrap the text if it's too long
        text_rect = QRectF(text_x, text_y, text_width, 120)
        painter.drawText(text_rect, Qt.TextWordWrap | Qt.AlignCenter, str(self.id))

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

    def make_group(self, z_value=0):
        """
        Make the DocObj a group.
        """
        self.group = True

        self.setZValue(z_value)

        self.setFlag(QGraphicsItem.ItemIsSelectable)
        self.setFlag(QGraphicsItem.ItemIsMovable, False)
    
    def make_final(self):
        """
        Make the DocObj a final node.
        """
        self.group = False

        self.setZValue(99)
        #self.setPos(QPointF(x, y))
        self.setFlag(QGraphicsItem.ItemIsMovable)
        self.setFlag(QGraphicsItem.ItemIsSelectable)
    
    def get_sources(self):
        return [line.source_doc for line in self.inbound_lines]
    
    #def add_source(self, source):
    #    self.sources.append(Line(source, self))
    
    def get_sinks(self):
        return [line.sink_doc for line in self.outbound_lines]
    
    #def add_sink(self, sink):
    #    self.outbound_lines.append(Line(self, sink))
    
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
        self.propagate_postion_up(False) #does not include self in the updating position, as it is already final not a grup

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
        self.propagate_postion_up()
        self.expandable = False

    def change_icon(self, icon_path):
        """
        Change the icon of the object.

        Args:
            icon_path (str): The path to the new icon.
        """
        self.payload["icon"] = icon_path
        self.__select_square()
        self.__update_viz()
        self.update()

    def context_change_icon(self):
        """
        Change the icon of the object.
        """
        icon_file, _ = QFileDialog.getOpenFileName(None, "Select Icon", "", "Icon Files (*.ico *.jpg *.jpeg *.png)")
        
        if icon_file:
            relative_path = os.path.relpath(icon_file, os.getcwd())
            self.change_icon(relative_path)

    def open_in_browser(self):
        """
        Open the object in the default web browser.
        """
        link = self.payload.get("link")
        if link:
            import webbrowser
            webbrowser.open(link)
        else:
            print("No link specified for this object.")

    def contextMenuEvent(self, event):
        """
        Show a context menu when the user right-clicks on the object.
        """
        ContextMenu(self, event)
        