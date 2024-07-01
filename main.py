import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QGraphicsView, QWidget, QGraphicsScene,QVBoxLayout, QHBoxLayout, QTextEdit, QPushButton, QGraphicsRectItem
from PyQt5.QtGui import QPainter, QColor
from PyQt5.QtCore import Qt

from load_documentation import load_documentation
from draw_visualization import drawRootVisualization

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

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

    def load_documentation_wrapper(self):
        self.docs_obj_dict = load_documentation()
        for doc_obj in self.docs_obj_dict.values():
            self.__draw_viz(doc_obj)
        
        self.main_part.scene().update()

    def __draw_viz(self, node):
        self.main_part.scene().addItem(node)
        for line in node.outbound_lines:
            self.main_part.scene().addItem(line)

class SideBar(QWidget):
    def __init__(self, window):
        super().__init__()
        self.main_part = window.main_part
        self.root_nodes = None

        # Create a text area in the sidebar
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Enter text here...")

        # Create a vertical layout for the sidebar and add the text area to it
        sidebar_layout = QVBoxLayout()
        sidebar_layout.addWidget(self.text_area)

        load_button = QPushButton("Load Documentation")
        load_button.clicked.connect(window.load_documentation_wrapper)
        sidebar_layout.addWidget(load_button)


        self.setLayout(sidebar_layout)

class MainPart(QGraphicsView):
    def __init__(self, window):
        super().__init__(window.scene)

        self.setFixedWidth(500)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    window.load_documentation_wrapper()
    sys.exit(app.exec())

