import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QWidget, QGraphicsScene,QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QImage
from PyQt5.QtCore import QRectF, Qt

from load_documentation import load_documentation
from save_documentation import save_documentation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the size of the main window
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and set it as the central widget
        main_widget = QWidget()
        self.setCentralWidget(main_widget)

        # Create the layout for the main widget
        main_layout = QHBoxLayout()
        main_widget.setLayout(main_layout)

        # Create the main part widget and add it to the main layout
        self.scene = QGraphicsScene()
        self.main_part = MainPart(self)
        self.main_part.setViewportUpdateMode(QGraphicsView.FullViewportUpdate)
        main_layout.addWidget(self.main_part)

        # Create the sidebar widget and add it to the main layout
        self.sidebar = SideBar(self)
        main_layout.addWidget(self.sidebar)

    def load_documentation_wrapper(self, filter_group=None):
        self.scene.clear()
        self.docs_obj_dict = load_documentation()
        for doc_obj in self.docs_obj_dict.values():
            if filter_group and doc_obj.id != filter_group:
                continue
            self.__draw_viz(doc_obj)
        
        self.scene.update()

    def save_documentation_wrapper(self):
        save_documentation(self.docs_obj_dict)

    def change_id_wrapper(self):
        selected_obj = self.main_part.scene().selectedItems()[0]
        old_id = selected_obj.id
        new_id = self.sidebar.id_line.toPlainText()
        selected_obj.id = new_id
        del self.docs_obj_dict[old_id]
        self.docs_obj_dict[new_id] = selected_obj

        for sink in selected_obj.get_sinks():
            sink.payload["sources"] = [new_id if source == old_id else source for source in sink.payload.get("sources",[])]

    def __draw_viz(self, node):
        self.main_part.scene().addItem(node)
        for line in node.outbound_lines:
            self.main_part.scene().addItem(line)     

    def export_scene_to_jpg(self, filename, filter_group=None):
        # Create a QImage object with the same size as the scene
        # If a filter group is specified, propagate the filter down the tree, think if this shouldnt be done on the filtering level
        if filter_group:
            root_nodes = [doc_obj for doc_obj in self.docs_obj_dict.values() if not doc_obj.parent_doc]
            for root_node in root_nodes:
                    self.__propagate_filter_down(root_node, filter_group)

        image = QImage(int(self.scene.width()), int(self.scene.height()), QImage.Format_ARGB32)
        image.fill(Qt.white)  # Fill the image with white

        # Create a QPainter object and render the scene into the image
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()

        # Save the image to a file
        image.save(filename)

class SideBar(QWidget):
    def __init__(self, window):
        super().__init__()

        self.setFixedWidth(300)

        self.main_part = window.main_part
        self.root_nodes = None

        # Create vertical layout for the sidebar
        sidebar_layout = QVBoxLayout()

        # Create text line for showing and editing ID
        self.id_line = QTextEdit(self)
        self.id_line.setMaximumHeight(self.id_line.fontMetrics().height()+5)
        sidebar_layout.addWidget(self.id_line)

        change_id_button = QPushButton("Change ID")
        change_id_button.clicked.connect(window.change_id_wrapper)
        sidebar_layout.addWidget(change_id_button)

        # Create a text area in the sidebar
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Enter text here...")    
        
        sidebar_layout.addWidget(self.text_area)

        load_button = QPushButton("Load Documentation")
        load_button.clicked.connect(window.load_documentation_wrapper)
        sidebar_layout.addWidget(load_button)

        save_button = QPushButton("Save Documentation")
        save_button.clicked.connect(window.save_documentation_wrapper)
        sidebar_layout.addWidget(save_button)

        self.setLayout(sidebar_layout)

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
        if event.button() == Qt.LeftButton and not [obj for obj in self.scene().selectedItems() if not obj.group]:
            self._is_panning = True
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()

    def mouseMoveEvent(self, event):
        if self._is_panning:
            dx = self._pan_start_x - event.x()
            dy = self._pan_start_y - event.y()
            self._pan_start_x = event.x()
            self._pan_start_y = event.y()
            self.horizontalScrollBar().setValue(self.horizontalScrollBar().value() + dx)
            self.verticalScrollBar().setValue(self.verticalScrollBar().value() + dy)
        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() == Qt.LeftButton:
            self._is_panning = False
        super().mouseReleaseEvent(event)

import argparse

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument('--export', action='store_true')
    parser.add_argument('--group')
    args = parser.parse_args()


    app = QApplication(sys.argv)
    window = MainWindow()

    window.load_documentation_wrapper()

    if args.export:
        if not args.group:
            print("Warning: The --export flag was used without the --group flag. The scene was exported to a JPG but might be very big")
        window.export_scene_to_jpg('output.jpg', args.group)  # Export the scene to a JPG image

        sys.exit(0)

    window.show()
    sys.exit(app.exec())

