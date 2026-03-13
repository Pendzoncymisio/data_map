from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QAction, QImage, QKeySequence, QPainter
from PyQt6.QtWidgets import (
    QGraphicsScene,
    QGraphicsView,
    QLabel,
    QMainWindow,
    QSplitter,
    QStatusBar,
    QToolBar,
)

import theme
from load_config import load_config
from load_documentation import load_documentation
from main_part import MainPart
from save_documentation import save_documentation
from side_bar import SideBar

try:
    from git import Repo

    GIT_AVAILABLE = True
except ImportError:
    GIT_AVAILABLE = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("DataMap")
        self.setGeometry(80, 80, 1400, 900)
        self.setMinimumSize(960, 640)

        self.scene = QGraphicsScene()
        self.active_obj = None

        self._build_central_widget()
        self._build_menu_bar()
        self._build_toolbar()
        self._build_status_bar()

    # ── Layout construction ──────────────────────────────────────────────────

    def _build_menu_bar(self):
        mb = self.menuBar()

        # File
        file_menu = mb.addMenu("  File  ")

        act_load = QAction("Load Documentation", self)
        act_load.setShortcut(QKeySequence("Ctrl+O"))
        act_load.triggered.connect(self.load_documentation_wrapper)
        file_menu.addAction(act_load)

        act_save = QAction("Save Documentation", self)
        act_save.setShortcut(QKeySequence("Ctrl+S"))
        act_save.triggered.connect(self.save_documentation_wrapper)
        file_menu.addAction(act_save)

        file_menu.addSeparator()

        act_export = QAction("Export as JPG...", self)
        act_export.triggered.connect(lambda: self.export_scene_to_jpg("output.jpg"))
        file_menu.addAction(act_export)

        file_menu.addSeparator()

        act_exit = QAction("Quit", self)
        act_exit.setShortcut(QKeySequence("Ctrl+Q"))
        act_exit.triggered.connect(self.close)
        file_menu.addAction(act_exit)

        # Edit
        edit_menu = mb.addMenu("  Edit  ")

        act_commit = QAction("Commit Changes", self)
        act_commit.setShortcut(QKeySequence("Ctrl+Shift+C"))
        act_commit.triggered.connect(self.commit_wrapper)
        edit_menu.addAction(act_commit)

        # View
        view_menu = mb.addMenu("  View  ")

        act_zoom_in = QAction("Zoom In", self)
        act_zoom_in.setShortcut(QKeySequence("Ctrl+="))
        act_zoom_in.triggered.connect(lambda: self.main_part.zoom_step(+1))
        view_menu.addAction(act_zoom_in)

        act_zoom_out = QAction("Zoom Out", self)
        act_zoom_out.setShortcut(QKeySequence("Ctrl+-"))
        act_zoom_out.triggered.connect(lambda: self.main_part.zoom_step(-1))
        view_menu.addAction(act_zoom_out)

        act_reset = QAction("Reset Zoom", self)
        act_reset.setShortcut(QKeySequence("Ctrl+0"))
        act_reset.triggered.connect(self.main_part.reset_zoom)
        view_menu.addAction(act_reset)

        act_fit = QAction("Fit to View", self)
        act_fit.setShortcut(QKeySequence("Ctrl+Shift+F"))
        act_fit.triggered.connect(self.main_part.fit_view)
        view_menu.addAction(act_fit)

    def _build_toolbar(self):
        tb = QToolBar("Main Toolbar")
        tb.setMovable(False)
        tb.setObjectName("main_toolbar")
        self.addToolBar(tb)

        def act(label, tip, slot):
            a = QAction(label, self)
            a.setToolTip(tip)
            a.triggered.connect(slot)
            tb.addAction(a)
            return a

        act("  ⟳  Load", "Load Documentation  (Ctrl+O)", self.load_documentation_wrapper)
        act("  ↓  Save", "Save Documentation  (Ctrl+S)", self.save_documentation_wrapper)

        tb.addSeparator()

        act("  -", "Zoom Out  (Ctrl+-)", lambda: self.main_part.zoom_step(-1))

        self._zoom_label = QLabel("  100%  ")
        self._zoom_label.setStyleSheet(
            f"color: {theme.TEXT_SECONDARY}; font-size: 12px;"
            f" min-width: 50px; text-align: center; border: none;"
        )
        tb.addWidget(self._zoom_label)

        act("  +", "Zoom In  (Ctrl+=)", lambda: self.main_part.zoom_step(+1))
        act("  ⊡  Fit", "Fit all items to view  (Ctrl+Shift+F)", self.main_part.fit_view)

        tb.addSeparator()

        act("  ✓  Commit", "Commit changes to git", self.commit_wrapper)

    def _build_central_widget(self):
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.setChildrenCollapsible(False)
        splitter.setHandleWidth(1)
        self.setCentralWidget(splitter)

        self.main_part = MainPart(self)
        self.main_part.setViewportUpdateMode(QGraphicsView.ViewportUpdateMode.FullViewportUpdate)
        self.main_part.zoom_changed.connect(self._on_zoom_changed)
        splitter.addWidget(self.main_part)

        self.sidebar = SideBar(self)
        splitter.addWidget(self.sidebar)

        splitter.setSizes([1060, 320])
        splitter.setStretchFactor(0, 1)
        splitter.setStretchFactor(1, 0)

    def _build_status_bar(self):
        sb = QStatusBar()
        sb.setSizeGripEnabled(False)
        self.setStatusBar(sb)

        lbl_style = (
            f"color: {theme.TEXT_SECONDARY}; background: transparent;"
            f" font-size: 11px; padding: 0 10px;"
            f" border-right: 1px solid {theme.BORDER};"
        )

        self._lbl_mode = QLabel("Ready")
        self._lbl_items = QLabel("0 nodes")
        self._lbl_zoom = QLabel("100%")
        self._lbl_msg = QLabel("")

        for lbl in (self._lbl_mode, self._lbl_items, self._lbl_zoom):
            lbl.setStyleSheet(lbl_style)
            sb.addPermanentWidget(lbl)

        self._lbl_msg.setStyleSheet(
            f"color: {theme.TEXT_SECONDARY}; background: transparent;"
            f" font-size: 11px; padding: 0 10px;"
        )
        sb.addWidget(self._lbl_msg)

    # ── Signal handlers ──────────────────────────────────────────────────────

    def _on_zoom_changed(self, pct: int):
        self._zoom_label.setText(f"  {pct}%  ")
        self._lbl_zoom.setText(f"{pct}%")

    def _flash(self, msg: str, ms: int = 4000):
        self._lbl_msg.setText(msg)
        QTimer.singleShot(ms, lambda: self._lbl_msg.setText(""))

    def update_item_count(self):
        # count only DocObj items (avoid Line items in count)
        try:
            from doc_obj import DocObj

            n = sum(1 for it in self.scene.items() if isinstance(it, DocObj))
        except Exception:
            n = len(self.scene.items())
        self._lbl_items.setText(f"{n} nodes")

    # ── Public API (unchanged signatures) ───────────────────────────────────

    def load_documentation_wrapper(self, filter_group=None):
        self.scene.clear()
        self.docs_obj_dict = load_documentation()
        for doc_obj in self.docs_obj_dict.values():
            if (
                filter_group
                and doc_obj.id != filter_group
                and (doc_obj.parent_doc is None or doc_obj.parent_doc.id != filter_group)
            ):
                continue
            self.__draw_viz(doc_obj)
        self.scene.update()
        self.update_item_count()
        self._flash("Documentation loaded")

    def save_documentation_wrapper(self):
        save_documentation(self.docs_obj_dict)
        self._flash("Documentation saved")

    def commit_wrapper(self):
        if not GIT_AVAILABLE:
            self._flash("GitPython not available")
            return
        msg = self.sidebar.commit_line.toPlainText().strip()
        if not msg:
            self._flash("Enter a commit message first")
            return
        try:
            repo = Repo(load_config("doc_path"))
            repo.git.add(update=True)
            repo.index.commit(msg)
            self.sidebar.commit_line.clear()
            self._flash(f"Committed: {msg[:50]}")
        except Exception as exc:
            self._flash(f"Commit failed: {exc}")

    def change_id_wrapper(self):
        items = self.main_part.scene().selectedItems()
        if not items:
            self._flash("No item selected")
            return
        obj = items[0]
        old_id = obj.id
        new_id = self.sidebar.id_line.toPlainText().strip()
        if not new_id:
            self._flash("ID cannot be empty")
            return
        if new_id == old_id:
            return
        obj.id = new_id
        del self.docs_obj_dict[old_id]
        self.docs_obj_dict[new_id] = obj
        for sink in obj.get_sinks():
            sink.payload["sources"] = [
                new_id if s == old_id else s for s in sink.payload.get("sources", [])
            ]
        obj.update()
        self._flash(f"Renamed: {old_id} → {new_id}")

    def change_source_file_wrapper(self):
        items = self.main_part.scene().selectedItems()
        if not items:
            self._flash("No item selected")
            return
        obj = items[0]
        new_path = self.sidebar.source_file_line.toPlainText().strip()
        if not new_path.endswith(".json"):
            self._flash("Path must end with .json")
            return
        obj.source_file = new_path
        self._flash("Source file updated")

    def __draw_viz(self, node):
        self.main_part.scene().addItem(node)
        for line in node.outbound_lines:
            self.main_part.scene().addItem(line)

    def export_scene_to_jpg(self, filename, filter_group=None):
        image = QImage(
            int(self.scene.width()), int(self.scene.height()), QImage.Format.Format_ARGB32
        )
        image.fill(Qt.GlobalColor.white)
        painter = QPainter(image)
        self.scene.render(painter)
        painter.end()
        image.save(filename)
        self._flash(f"Exported → {filename}")
