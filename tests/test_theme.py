"""Regression tests for theme.py — no Qt required."""

import re

import pytest

import theme

HEX_RE = re.compile(r"^#[0-9A-Fa-f]{6}([0-9A-Fa-f]{2})?$")

COLOR_TOKENS = [
    "BG_PRIMARY",
    "BG_SECONDARY",
    "BG_TERTIARY",
    "BG_ELEVATED",
    "BORDER",
    "BORDER_LIGHT",
    "ACCENT",
    "ACCENT_HOVER",
    "ACCENT_PRESSED",
    "ACCENT_SUBTLE",
    "ACCENT_DIM",
    "TEXT_PRIMARY",
    "TEXT_SECONDARY",
    "TEXT_MUTED",
    "SUCCESS",
    "SUCCESS_SUBTLE",
    "WARNING",
    "ERROR",
    "ERROR_SUBTLE",
    "NODE_BG",
    "NODE_BORDER",
    "NODE_BORDER_GROUP",
    "NODE_SELECTED",
    "NODE_SHADOW",
    "GROUP_FILL",
    "LINE_COLOR",
    "LINE_ARROW",
    "CANVAS_BG",
    "CANVAS_DOT",
    "SB_TRACK",
    "SB_HANDLE",
    "SB_HANDLE_HOVER",
]

CSS_SELECTORS = [
    "QWidget",
    "QPushButton",
    "QLineEdit",
    "QTextEdit",
    "QMenuBar",
    "QMenu",
    "QToolBar",
    "QStatusBar",
    "QGraphicsView",
    "QScrollBar",
    "QToolButton",
    "QLabel",
]


@pytest.mark.unit
@pytest.mark.parametrize("token", COLOR_TOKENS)
def test_color_token_is_valid_hex(token):
    value = getattr(theme, token)
    assert isinstance(value, str), f"{token} must be a str, got {type(value)}"
    assert HEX_RE.match(value), f"{token}={value!r} is not a valid #RRGGBB or #RRGGBBAA hex color"


@pytest.mark.unit
def test_stylesheet_non_empty():
    assert isinstance(theme.STYLESHEET, str)
    assert len(theme.STYLESHEET) > 200


@pytest.mark.unit
@pytest.mark.parametrize("selector", CSS_SELECTORS)
def test_stylesheet_contains_selector(selector):
    assert selector in theme.STYLESHEET, f"CSS selector {selector!r} missing from STYLESHEET"


@pytest.mark.unit
def test_stylesheet_balanced_braces():
    opens = theme.STYLESHEET.count("{")
    closes = theme.STYLESHEET.count("}")
    assert opens == closes, f"Unbalanced braces: {opens} '{{' vs {closes} '}}'"


@pytest.mark.unit
def test_font_ui_is_nonempty_string():
    assert isinstance(theme.FONT_UI, str)
    assert theme.FONT_UI.strip()


@pytest.mark.unit
def test_accent_distinct_from_bg():
    """Accent color must be visibly different from all background colors."""
    bg_tokens = ["BG_PRIMARY", "BG_SECONDARY", "BG_TERTIARY", "BG_ELEVATED"]
    for tok in bg_tokens:
        assert theme.ACCENT != getattr(theme, tok), f"ACCENT should not equal {tok}"
