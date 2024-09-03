import os
import json

from PyQt6.QtWidgets import QGraphicsItem, QFileDialog
from PyQt6.QtCore import Qt, QRectF, QSizeF, QPointF
from PyQt6.QtGui import QPixmap, QColor

from line import Line
from context_menu import ContextMenu

class DocObj(QGraphicsItem):
    def __init__(self, id, payload, docs_obj_dict, source_file):
        super().__init__()
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemSendsGeometryChanges)

        self.id = id
        self.payload = payload

        self.docs_obj_dict = docs_obj_dict # Store reference to the dictionary of all DocObj objects
        docs_obj_dict[id] = self # Object itself is responsible to add itself to the dictionary

        self.source_file = source_file

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

        self.adding_line_to = False
        self.adding_line_from = False

    def __update_viz(self):
        #TODO: Everything in viz should update, and icon should be on viz level
        self.icon = self.payload.get("icon", "default_icon.png")  

    def itemChange(self, change, value):
        if change == QGraphicsItem.GraphicsItemChange.ItemPositionChange:
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
        
        elif change == QGraphicsItem.GraphicsItemChange.ItemSelectedChange:
            scene = self.scene()
            view = scene.views()[0]
            window = view.window() if view else None
            if value:
                if window.active_obj and (window.active_obj.adding_line_to or window.active_obj.adding_line_from):
                    if window.active_obj.adding_line_to:
                        self.add_line_to_select(window.active_obj)
                        print("Adding line from",self.id, " to ", window.active_obj.id)
                    elif window.active_obj.adding_line_from:
                        print("Adding line from",window.active_obj.id , " to ", self.id)
                        self.add_line_from_select(window.active_obj)
                    else:
                        print("Error: Invalid state - neither adding line to or from")
                self.__select_square()
                return value
            else:
                self.__deselect_square()
        
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

    def propagate_postion_down(self, z_value=0, parent_pos=None):
        """
        Propagates the position down to the child documents recursively.

        Args:
            z_value (int): The z-value to set for the document.
            parent_pos (dict): The absolute position of the parent document.

        Returns:
            None
        """
        self.prepareGeometryChange()
        self.setZValue(z_value)
        pos = self.position_rel_to_abs(parent_pos)
        self.setPos(pos["x"], pos["y"])
        self.update()

        #print(self.id, "my", self.pos().x(), self.pos().y(), "rel", self.rel_x, self.rel_y, "parent", (self.parent_doc.id, self.parent_doc.pos().x(), self.parent_doc.pos().y()) if self.parent_doc else None)
        for line in self.outbound_lines + self.inbound_lines:
                line.update_position()
        for child in self.children_docs:
            child.propagate_postion_down(z_value + 1, parent_pos=pos)

    def position_rel_to_abs(self, parent_pos=None):
        """
        Converts the relative position of the document object to absolute position.

        Args:
            parent_pos (dict): The parent position dictionary containing 'x' and 'y' coordinates. 
                               Defaults to None if the document object has no parent.
                               It has to be done that way because parent.pos() is not properly updated yet.

        Returns:
            dict: The absolute position dictionary containing 'x' and 'y' coordinates.
        """
        if self.parent_doc:
            abs_x = self.rel_x + parent_pos["x"]
            abs_y = self.rel_y + parent_pos["y"]
            return {"x": abs_x, "y": abs_y}
        else:
            return {"x": self.rel_x, "y": self.rel_y}

    def position_abs_to_rel(self):
        if self.parent_doc:
            rel_x = self.pos().x() - self.parent_doc.pos().x()
            rel_y = self.pos().y() - self.parent_doc.pos().y()
            return {"x": rel_x, "y": rel_y}
        else:
            return {"x": self.pos().x(), "y": self.pos().y()}
    
    def paint(self, painter, option, widget):
        if self.group:
            rect = self.boundingRect()
            painter.setPen(QColor("black"))
            # painter.setBrush(Qt.white)
            painter.drawRoundedRect(rect, 10, 10)

            icon_size = QSizeF(QPixmap(self.icon).size())
            #icon_rect = QRectF(rect.topRight(), icon_size)
            icon_rect = QRectF(rect.topRight(),QSizeF(50,50))
            painter.drawPixmap(icon_rect, QPixmap(self.icon), QRectF(QPixmap(self.icon).rect()))
            return

        pixmap = QPixmap(self.icon)
        painter.drawPixmap(self.boundingRect(), pixmap, QRectF(pixmap.rect()))

        # Calculate the width of the text
        text_width = painter.fontMetrics().horizontalAdvance(str(self.id))

        # Calculate the position to display the text
        #text_x = self.boundingRect().center().x() - text_width / 2
        text_width = 120
        text_x = self.boundingRect().center().x() - text_width / 2
        text_y = self.boundingRect().bottom() + 10

        # Wrap the text if it's too long
        if self.isSelected():
            text_height = 180
        else:
            text_height = 20
        text_rect = QRectF(text_x, text_y, text_width, text_height)
        painter.drawText(text_rect, Qt.TextFlag.TextWordWrap | Qt.AlignmentFlag.AlignHCenter | Qt.AlignmentFlag.AlignTop, str(self.id))

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

        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable, True)
    
    def make_final(self):
        """
        Make the DocObj a final node.
        """
        self.group = False

        self.setZValue(99)
        #self.setPos(QPointF(x, y))
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsMovable)
        self.setFlag(QGraphicsItem.GraphicsItemFlag.ItemIsSelectable)
    
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
        window.active_obj = self
        window.sidebar.text_area.setText(json.dumps(self.payload, indent=2))
        window.sidebar.id_line.setText(self.id)
        window.sidebar.source_file_line.setText(self.source_file)
        print("Square selected!", self.id, self.zValue())

    
    def __deselect_square(self):
        scene = self.scene()
        view = scene.views()[0]
        window = view.window() if view else None
        #window.active_obj = None
        text = window.sidebar.text_area.toPlainText()
        if text:
            window.sidebar.text_area.clear()
            #TODO: Think if that should be done as doc_ref.update_payload(payload)
            try:
                self.payload = json.loads(text)
            except json.JSONDecodeError:
                print("Invalid JSON, try again it.")
            # TODO: Handle changing of the ID without confirming
            window.sidebar.id_line.clear()
            window.sidebar.source_file_line.clear()
            self.__update_viz()
        else:
            print("No text in the text area - if you want to delete the node, press the delete button.")
        print("Square deselected!")

    def create_new_source(self):
        new_obj = DocObj("new", {"icon": "default_icon.png", "viz": {"x": self.pos().x(), "y": self.pos().y() - 100}}, self.docs_obj_dict, self.source_file)
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() - 100)
        line = Line(new_obj, self)
        new_obj.outbound_lines.append(line)
        self.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
        
        if "sources" in self.payload:
            self.payload["sources"].append(new_obj.id)
        else:
            self.payload["sources"] = [new_obj.id]
        
        return new_obj
    
    def create_new_sink(self):
        new_obj = DocObj("new", {"icon": "default_icon.png", "sources":[self.id], "viz": {"x": self.pos().x(), "y": self.pos().y() + 100}}, self.docs_obj_dict, self.source_file)
        new_obj.make_final()
        new_obj.setPos(self.pos().x(),self.pos().y() + 100)
        line = Line(self, new_obj)
        self.outbound_lines.append(line)
        new_obj.inbound_lines.append(line)
        self.scene().addItem(line)
        self.scene().addItem(new_obj)
        return new_obj
    
    def add_line_to(self):
        self.adding_line_to = True

    def add_line_from(self):
        self.adding_line_from = True

    def add_line_to_select(self, obj_to):
        if obj_to == self:
            print("Cannot connect to self.")
            return
        if obj_to in self.get_sources():
            print("Already connected.")
            return
        line = Line(self, obj_to)
        self.outbound_lines.append(line)
        obj_to.inbound_lines.append(line)
        self.scene().addItem(line)
        self.adding_line_to = False

    def add_line_from_select(self, obj_from):
        if obj_from == self:
            print("Cannot connect to self.")
            return
        if obj_from in self.get_sinks():
            print("Already connected.")
            return
        line = Line(obj_from, self)
        self.inbound_lines.append(line)
        obj_from.outbound_lines.append(line)
        self.scene().addItem(line)
        obj_from.adding_line_from = False

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
        base_z = 0
        if self.parent_doc:
            base_z = self.parent_doc.zValue() + 1
        self.setZValue(base_z)
        self.propagate_postion_down(base_z, {"x": self.pos().x(), "y": self.pos().y()})

        for child in self.children_docs:
            child.setVisible(True)
        for line in child.outbound_lines + child.inbound_lines:
            line.setVisible(True)

        # Make the object behave as a group again
        self.make_group()
        self.propagate_postion_up()
        self.expandable = False

    def set_group(self, group):
        group_obj = self.docs_obj_dict[group]
        group_obj.add_child_document(self)
        self.parent_doc = group_obj

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
        self.__select_square()
        ContextMenu(self, event)
        