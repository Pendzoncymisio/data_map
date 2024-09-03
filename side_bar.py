from PyQt6.QtWidgets import QWidget, QVBoxLayout, QTextEdit, QPushButton

class SideBar(QWidget):
    def __init__(self, window):
        super().__init__()

        self.main_part = window.main_part
        self.root_nodes = None

        # Create vertical layout for the sidebar
        sidebar_layout = QVBoxLayout()

        # Create text line for showing and editing ID
        self.id_line = QTextEdit(self)
        self.id_line.setMaximumHeight(self.id_line.fontMetrics().height()*3+15)
        sidebar_layout.addWidget(self.id_line)

        change_id_button = QPushButton("Change ID")
        change_id_button.clicked.connect(window.change_id_wrapper)
        sidebar_layout.addWidget(change_id_button)

        # Create a text area in the sidebar
        self.text_area = QTextEdit(self)
        self.text_area.setPlaceholderText("Enter text here...")    
        
        sidebar_layout.addWidget(self.text_area)

        # Create text bar for the source_file path
        self.source_file_line = QTextEdit(self)
        self.source_file_line.setMaximumHeight(self.source_file_line.fontMetrics().height()+5)
        sidebar_layout.addWidget(self.source_file_line)

        #Create button to change source file
        change_source_file_button = QPushButton("Change Source File")
        change_source_file_button.clicked.connect(window.change_source_file_wrapper)
        sidebar_layout.addWidget(change_source_file_button)

        load_button = QPushButton("Load Documentation")
        load_button.clicked.connect(window.load_documentation_wrapper)
        sidebar_layout.addWidget(load_button)

        save_button = QPushButton("Save Documentation")
        save_button.clicked.connect(window.save_documentation_wrapper)
        sidebar_layout.addWidget(save_button)

        # Create text line for commit message
        self.commit_line = QTextEdit(self)
        self.commit_line.setMaximumHeight(self.commit_line.fontMetrics().height()+5)
        sidebar_layout.addWidget(self.commit_line)

        commit_button = QPushButton("Commit")
        commit_button.clicked.connect(window.commit_wrapper)
        sidebar_layout.addWidget(commit_button)

        self.setLayout(sidebar_layout)