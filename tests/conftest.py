"""Shared pytest fixtures for the data_map test suite."""

import json
import os
from unittest.mock import MagicMock

import pytest

# Must be set BEFORE any Qt import so Qt uses the offscreen (headless) backend.
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")

from PyQt6.QtWidgets import QGraphicsScene, QGraphicsView  # noqa: E402


class _MockSceneView(QGraphicsView):
    """QGraphicsView that returns a MagicMock as its top-level window.

    DocObj internally calls ``self.scene().views()[0].window()`` to reach the
    MainWindow for sidebar updates.  This subclass intercepts that call so
    unit tests don't need a real MainWindow.
    """

    def __init__(self, scene: QGraphicsScene) -> None:
        super().__init__(scene)
        mock_win = MagicMock()
        mock_win.active_obj = None
        # Make toPlainText() return "" so __deselect_square takes the safe branch
        mock_win.sidebar.text_area.toPlainText.return_value = ""
        self._mock_win = mock_win

    def window(self):  # type: ignore[override]
        return self._mock_win


# ---------------------------------------------------------------------------
# Qt fixtures
# ---------------------------------------------------------------------------


@pytest.fixture(scope="session")
def qapp():
    """Session-scoped QApplication (pytest-qt also provides this; we keep ours
    so tests that don't use qtbot still have a running app instance)."""
    from PyQt6.QtWidgets import QApplication

    app = QApplication.instance()
    if app is None:
        app = QApplication([])
    return app


@pytest.fixture
def scene_view(qapp):
    """Return (QGraphicsScene, _MockSceneView, mock_window) for DocObj tests."""
    s = QGraphicsScene()
    v = _MockSceneView(s)
    return s, v, v._mock_win


# ---------------------------------------------------------------------------
# Documentation / file fixtures
# ---------------------------------------------------------------------------


@pytest.fixture
def simple_docs_dir(tmp_path):
    """Two nodes, node_b lists node_a as a source."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    data = {
        "node_a": {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}},
        "node_b": {
            "icon": "default_icon.png",
            "viz": {"x": 100, "y": 0},
            "sources": ["node_a"],
        },
    }
    (doc_dir / "main.json").write_text(json.dumps(data))
    return doc_dir


@pytest.fixture
def grouped_docs_dir(tmp_path):
    """A group node with two children."""
    doc_dir = tmp_path / "docs"
    doc_dir.mkdir()
    data = {
        "group_1": {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}},
        "child_a": {
            "icon": "default_icon.png",
            "viz": {"x": 20, "y": 20},
            "group": "group_1",
        },
        "child_b": {
            "icon": "default_icon.png",
            "viz": {"x": 80, "y": 20},
            "group": "group_1",
        },
    }
    (doc_dir / "main.json").write_text(json.dumps(data))
    return doc_dir


@pytest.fixture
def multi_file_docs_dir(tmp_path):
    """Documentation spread across two JSON files in different directories."""
    doc_dir = tmp_path / "docs"
    sub = doc_dir / "sub"
    sub.mkdir(parents=True)

    (doc_dir / "a.json").write_text(
        json.dumps({"node_x": {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}}})
    )
    (sub / "b.json").write_text(
        json.dumps(
            {
                "node_y": {
                    "icon": "default_icon.png",
                    "viz": {"x": 0, "y": 100},
                    "sources": ["node_x"],
                }
            }
        )
    )
    return doc_dir
