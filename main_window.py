from PyQt6.QtWidgets import QMainWindow, QGraphicsView, QGraphicsScene, QHBoxLayout, QSplitter
from PyQt6.QtGui import QPainter, QImage
from PyQt6.QtCore import Qt
from git import Repo

from side_bar import SideBar
from main_part import MainPart

from load_documentation import load_documentation
from save_documentation import save_documentation

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        # Set the size of the main window
        self.setGeometry(100, 100, 800, 600)

        # Create the main widget and set it as the central widget
        main_widget = QSplitter()
        self.setCentralWidget(main_widget)

        # Create the main part widget and add it to the main layout
        self.scene = QGraphicsScene()
        self.main_part = MainPart(self)
        self.main_part.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        main_widget.addWidget(self.main_part)

        # Create the sidebar widget and add it to the main layout
        self.sidebar = SideBar(self)
        main_widget.addWidget(self.sidebar)

    def load_documentation_wrapper(self, filter_group=None):
        self.scene.clear()
        self.docs_obj_dict = load_documentation()
        for doc_obj in self.docs_obj_dict.values():
            if filter_group and doc_obj.id != filter_group and doc_obj.parent_doc.id != filter_group:
                continue
            #TODO: Cascading filtering, now showing only 2 levels
            self.__draw_viz(doc_obj)
        
        self.scene.update()

    def save_documentation_wrapper(self):
        save_documentation(self.docs_obj_dict)

    def commit_wrapper(self):
        commit_message = self.sidebar.commit_line.toPlainText()
        if commit_message:
            #TODO: Taken from config
            repo = Repo("../documentation")
            repo.git.add(update=True)
            repo.index.commit(commit_message)
        else:
            print("Error: Please enter a commit message.")

    def change_id_wrapper(self):
        selected_obj = self.main_part.scene().selectedItems()[0]
        old_id = selected_obj.id
        new_id = self.sidebar.id_line.toPlainText()
        selected_obj.id = new_id
        del self.docs_obj_dict[old_id]
        self.docs_obj_dict[new_id] = selected_obj

        for sink in selected_obj.get_sinks():
            sink.payload["sources"] = [new_id if source == old_id else source for source in sink.payload.get("sources",[])]

    def change_source_file_wrapper(self):
        selected_obj = self.main_part.scene().selectedItems()[0]
        new_source_file_path = self.sidebar.source_file_line.toPlainText()
        if not new_source_file_path.endswith('.json'):
            print("Error: Invalid source file path format. Please provide a valid path to a JSON file.")
            return
        
        #TODO: Add check if object has already been saved in different file
        selected_obj.source_file = new_source_file_path

    def __draw_viz(self, node):
        self.main_part.scene().addItem(node)
        for line in node.outbound_lines:
            self.main_part.scene().addItem(line)     

    def export_scene_to_jpg(self, filename, filter_group=None):
        # Create a QImage object with the same size as the scene
        # If a filter group is specified, propagate the filter down the tree, think if this shouldnt be done on the filtering level
        """if filter_group:
            root_nodes = [doc_obj for doc_obj in self.docs_obj_dict.values() if not doc_obj.parent_doc]
            for root_node in root_nodes:
                    self.__propagate_filter_down(root_node, filter_group)
        """
        image = QImage(int(self.scene.width()), int(self.scene.height()), QImage.Format_ARGB32)
        image.fill(Qt.white)  # Fill the image with white

        # Create a QPainter object and render the scene into the image
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()

        # Save the image to a file
        image.save(filename)