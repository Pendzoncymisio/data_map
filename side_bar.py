from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QFrame,
    QHBoxLayout,
    QLabel,
    QPushButton,
    QScrollArea,
    QTextEdit,
    QVBoxLayout,
    QWidget,
)

import theme


def _make_section_label(text: str) -> QLabel:
    lbl = QLabel(text)
    lbl.setObjectName("lbl_section")
    return lbl


def _make_separator() -> QFrame:
    sep = QFrame()
    sep.setFrameShape(QFrame.Shape.HLine)
    sep.setFrameShadow(QFrame.Shadow.Plain)
    return sep


class SideBar(QWidget):
    """Redesigned properties panel — preserves all original attribute names."""

    def __init__(self, window):
        super().__init__()
        self.setObjectName("sidebar_container")
        self.setFixedWidth(300)
        self.setStyleSheet(f"background-color: {theme.BG_SECONDARY};")

        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)
        outer.setSpacing(0)

        # ── Header bar ──────────────────────────────────────────
        header = QWidget()
        header.setObjectName("section_header")
        header.setStyleSheet(
            f"background-color: {theme.BG_SECONDARY};" f" border-bottom: 1px solid {theme.BORDER};"
        )
        header.setFixedHeight(44)
        h_lay = QHBoxLayout(header)
        h_lay.setContentsMargins(16, 0, 16, 0)

        title = QLabel("Properties")
        title.setObjectName("lbl_title")
        title.setStyleSheet(
            f"background: transparent; color: {theme.TEXT_PRIMARY};"
            f" font-size: 14px; font-weight: 700;"
        )
        h_lay.addWidget(title)
        h_lay.addStretch()

        outer.addWidget(header)

        # ── Scrollable content ────────────────────────────────────
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(f"QScrollArea {{ background: {theme.BG_SECONDARY}; border: none; }}")

        content = QWidget()
        content.setStyleSheet(f"background-color: {theme.BG_SECONDARY};")
        lay = QVBoxLayout(content)
        lay.setContentsMargins(14, 14, 14, 20)
        lay.setSpacing(6)

        # ── Node ID ──────────────────────────────────────────────
        lay.addWidget(_make_section_label("NODE ID"))

        self.id_line = QTextEdit()
        self.id_line.setFixedHeight(36)
        self.id_line.setPlaceholderText("Node identifier…")
        lay.addWidget(self.id_line)

        btn_id = QPushButton("Apply ID")
        btn_id.setObjectName("btn_accent")
        btn_id.setFixedHeight(32)
        btn_id.clicked.connect(window.change_id_wrapper)
        lay.addWidget(btn_id)

        lay.addSpacing(4)
        lay.addWidget(_make_separator())
        lay.addSpacing(4)

        # ── Payload JSON ──────────────────────────────────────────
        lay.addWidget(_make_section_label("PAYLOAD (JSON)"))

        self.text_area = QTextEdit()
        self.text_area.setPlaceholderText('{\n  "icon": "path/to/icon.png"\n}')
        self.text_area.setMinimumHeight(180)
        lay.addWidget(self.text_area)

        lay.addSpacing(4)
        lay.addWidget(_make_separator())
        lay.addSpacing(4)

        # ── Source File ───────────────────────────────────────────
        lay.addWidget(_make_section_label("SOURCE FILE"))

        self.source_file_line = QTextEdit()
        self.source_file_line.setFixedHeight(36)
        self.source_file_line.setPlaceholderText("path/to/file.json")
        lay.addWidget(self.source_file_line)

        btn_src = QPushButton("Update Source File")
        btn_src.setFixedHeight(32)
        btn_src.clicked.connect(window.change_source_file_wrapper)
        lay.addWidget(btn_src)

        lay.addSpacing(4)
        lay.addWidget(_make_separator())
        lay.addSpacing(4)

        # ── Documentation actions ─────────────────────────────────
        lay.addWidget(_make_section_label("DOCUMENTATION"))

        doc_row = QHBoxLayout()
        doc_row.setSpacing(6)

        btn_load = QPushButton("⟳  Load")
        btn_load.setFixedHeight(32)
        btn_load.clicked.connect(window.load_documentation_wrapper)

        btn_save = QPushButton("↓  Save")
        btn_save.setObjectName("btn_accent")
        btn_save.setFixedHeight(32)
        btn_save.clicked.connect(window.save_documentation_wrapper)

        doc_row.addWidget(btn_load)
        doc_row.addWidget(btn_save)
        lay.addLayout(doc_row)

        lay.addSpacing(4)
        lay.addWidget(_make_separator())
        lay.addSpacing(4)

        # ── Git commit ────────────────────────────────────────────
        lay.addWidget(_make_section_label("GIT COMMIT"))

        self.commit_line = QTextEdit()
        self.commit_line.setFixedHeight(36)
        self.commit_line.setPlaceholderText("Commit message…")
        lay.addWidget(self.commit_line)

        btn_commit = QPushButton("✓  Commit")
        btn_commit.setObjectName("btn_success")
        btn_commit.setFixedHeight(32)
        btn_commit.clicked.connect(window.commit_wrapper)
        lay.addWidget(btn_commit)

        lay.addStretch()

        scroll.setWidget(content)
        outer.addWidget(scroll)
