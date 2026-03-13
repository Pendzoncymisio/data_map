"""
DataMap — UI Theme
Central color tokens and global Qt stylesheet.
"""

# ── Color Palette ─────────────────────────────────────────────
BG_PRIMARY = "#0B0D14"
BG_SECONDARY = "#13161F"
BG_TERTIARY = "#1A1D2A"
BG_ELEVATED = "#1E2130"

BORDER = "#252838"
BORDER_LIGHT = "#2E3250"

ACCENT = "#7C6AF6"
ACCENT_HOVER = "#9E8FFF"
ACCENT_PRESSED = "#5E52C9"
ACCENT_SUBTLE = "#1C1A3A"
ACCENT_DIM = "#2A2550"

TEXT_PRIMARY = "#E4E6F0"
TEXT_SECONDARY = "#7A7D94"
TEXT_MUTED = "#3E4055"

SUCCESS = "#3ECF8E"
SUCCESS_SUBTLE = "#0D2B20"
WARNING = "#F59E0B"
ERROR = "#E05252"
ERROR_SUBTLE = "#2A0E0E"

# Canvas / Nodes
NODE_BG = "#161A28"
NODE_BORDER = "#252C48"
NODE_BORDER_GROUP = "#3A3470"
NODE_SELECTED = "#7C6AF6"
NODE_SHADOW = "#040508"
GROUP_FILL = "#0E1020"
LINE_COLOR = "#2A2E52"
LINE_ARROW = "#5A52AA"

CANVAS_BG = "#090B11"
CANVAS_DOT = "#13162080"

# Scrollbars
SB_TRACK = "#0D0F18"
SB_HANDLE = "#20233A"
SB_HANDLE_HOVER = "#2E3254"

# ── Font (plain name for QFont) ────────────────────────────────
FONT_UI = "Segoe UI"

# ── Stylesheet ─────────────────────────────────────────────────
STYLESHEET = f"""
QWidget {{
    background-color: {BG_PRIMARY};
    color: {TEXT_PRIMARY};
    font-family: 'Segoe UI', 'Inter', 'SF Pro Display', 'Helvetica Neue', Arial, sans-serif;
    font-size: 13px;
    outline: none;
}}

QMainWindow, QDialog {{
    background-color: {BG_PRIMARY};
}}

/* ── Splitter ── */
QSplitter::handle {{
    background-color: {BORDER};
}}
QSplitter::handle:horizontal {{
    width: 1px;
}}
QSplitter::handle:hover {{
    background-color: {ACCENT};
}}

/* ── Menu Bar ── */
QMenuBar {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border-bottom: 1px solid {BORDER};
    padding: 2px 6px;
    spacing: 2px;
}}
QMenuBar::item {{
    background: transparent;
    padding: 5px 12px;
    border-radius: 4px;
}}
QMenuBar::item:selected {{
    background-color: {BG_TERTIARY};
}}
QMenuBar::item:pressed {{
    background-color: {ACCENT_SUBTLE};
    color: {ACCENT};
}}

/* ── Menu ── */
QMenu {{
    background-color: {BG_SECONDARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 8px;
    padding: 5px 4px;
}}
QMenu::item {{
    padding: 7px 28px 7px 14px;
    border-radius: 4px;
    margin: 1px 0;
}}
QMenu::item:selected {{
    background-color: {ACCENT_SUBTLE};
}}
QMenu::item:disabled {{
    color: {TEXT_MUTED};
}}
QMenu::separator {{
    height: 1px;
    background: {BORDER};
    margin: 4px 8px;
}}

/* ── Toolbar ── */
QToolBar {{
    background-color: {BG_SECONDARY};
    border-bottom: 1px solid {BORDER};
    padding: 3px 10px;
    spacing: 2px;
}}
QToolBar::separator {{
    background-color: {BORDER_LIGHT};
    width: 1px;
    margin: 5px 4px;
}}
QToolButton {{
    background-color: transparent;
    color: {TEXT_PRIMARY};
    border: none;
    border-radius: 5px;
    padding: 5px 10px;
    font-size: 13px;
    min-width: 32px;
    min-height: 28px;
}}
QToolButton:hover {{
    background-color: {BG_TERTIARY};
}}
QToolButton:pressed {{
    background-color: {ACCENT_SUBTLE};
}}
QToolButton:checked {{
    background-color: {ACCENT_SUBTLE};
    color: {ACCENT};
}}

/* ── Status Bar ── */
QStatusBar {{
    background-color: {BG_SECONDARY};
    color: {TEXT_SECONDARY};
    border-top: 1px solid {BORDER};
    font-size: 11px;
    padding: 0 6px;
    min-height: 22px;
}}
QStatusBar QLabel {{
    color: {TEXT_SECONDARY};
    background: transparent;
    font-size: 11px;
    padding: 0 6px;
    border-right: 1px solid {BORDER};
}}

/* ── Scrollbars ── */
QScrollBar {{
    background: {SB_TRACK};
    border: none;
}}
QScrollBar:horizontal {{
    height: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar:vertical {{
    width: 8px;
    margin: 0;
    border-radius: 4px;
}}
QScrollBar::handle {{
    background: {SB_HANDLE};
    border-radius: 4px;
}}
QScrollBar::handle:horizontal {{ min-width: 24px; }}
QScrollBar::handle:vertical {{ min-height: 24px; }}
QScrollBar::handle:hover {{ background: {SB_HANDLE_HOVER}; }}
QScrollBar::add-line, QScrollBar::sub-line,
QScrollBar::add-page, QScrollBar::sub-page {{
    background: none; width: 0; height: 0;
}}

/* ── Text Edit ── */
QTextEdit {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 5px 8px;
    selection-background-color: {ACCENT_SUBTLE};
    selection-color: {TEXT_PRIMARY};
    line-height: 1.5;
}}
QTextEdit:focus {{
    border-color: {ACCENT};
}}

/* ── Line Edit ── */
QLineEdit {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 5px 8px;
    min-height: 30px;
    selection-background-color: {ACCENT_SUBTLE};
}}
QLineEdit:focus {{
    border-color: {ACCENT};
}}

/* ── Buttons ── */
QPushButton {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 5px;
    padding: 6px 14px;
    font-size: 13px;
    font-weight: 500;
    min-height: 30px;
}}
QPushButton:hover {{
    background-color: {BORDER_LIGHT};
    border-color: {BORDER_LIGHT};
}}
QPushButton:pressed {{
    background-color: {ACCENT_SUBTLE};
    border-color: {ACCENT};
    color: {ACCENT};
}}
QPushButton:disabled {{
    color: {TEXT_MUTED};
    border-color: {BORDER};
}}
QPushButton#btn_accent {{
    background-color: {ACCENT};
    color: #FFFFFF;
    border: none;
    font-weight: 600;
}}
QPushButton#btn_accent:hover {{
    background-color: {ACCENT_HOVER};
}}
QPushButton#btn_accent:pressed {{
    background-color: {ACCENT_PRESSED};
}}
QPushButton#btn_danger {{
    background-color: transparent;
    color: {ERROR};
    border: 1px solid {ERROR};
}}
QPushButton#btn_danger:hover {{
    background-color: {ERROR_SUBTLE};
}}
QPushButton#btn_success {{
    background-color: transparent;
    color: {SUCCESS};
    border: 1px solid {SUCCESS};
}}
QPushButton#btn_success:hover {{
    background-color: {SUCCESS_SUBTLE};
}}

/* ── Labels ── */
QLabel {{
    background: transparent;
    color: {TEXT_SECONDARY};
}}
QLabel#lbl_section {{
    color: {TEXT_MUTED};
    font-size: 10px;
    font-weight: 700;
    letter-spacing: 1px;
    text-transform: uppercase;
    padding: 2px 0;
}}
QLabel#lbl_title {{
    color: {TEXT_PRIMARY};
    font-size: 14px;
    font-weight: 700;
}}

/* ── Tooltip ── */
QToolTip {{
    background-color: {BG_ELEVATED};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER_LIGHT};
    border-radius: 5px;
    padding: 4px 8px;
    font-size: 12px;
}}

/* ── Input Dialog ── */
QInputDialog {{ background-color: {BG_SECONDARY}; }}
QInputDialog QLineEdit {{
    background-color: {BG_TERTIARY};
    color: {TEXT_PRIMARY};
    border: 1px solid {BORDER};
    border-radius: 5px;
    padding: 5px 8px;
    min-height: 30px;
}}

/* ── Graphics View ── */
QGraphicsView {{
    background-color: {CANVAS_BG};
    border: none;
    outline: none;
}}

/* ── Frame separators ── */
QFrame[frameShape="4"],
QFrame[frameShape="5"] {{
    background-color: {BORDER};
    border: none;
    max-height: 1px;
    min-height: 1px;
}}

/* ── Sidebar container ── */
#sidebar_container {{
    background-color: {BG_SECONDARY};
    border-left: 1px solid {BORDER};
}}

/* ── Section headers ── */
#section_header {{
    background-color: {BG_SECONDARY};
    border-bottom: 1px solid {BORDER};
    padding: 10px 14px;
}}
"""
