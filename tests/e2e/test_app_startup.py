"""E2E tests: MainWindow starts up and reaches a usable state."""

import json

import pytest


def _make_doc_dir(tmp_path):
    d = tmp_path / "docs"
    d.mkdir()
    data = {
        "svc_a": {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}},
        "svc_b": {"icon": "default_icon.png", "viz": {"x": 200, "y": 0}, "sources": ["svc_a"]},
    }
    (d / "main.json").write_text(json.dumps(data))
    return d


def _patch(monkeypatch, doc_dir):
    import load_config as lc

    monkeypatch.setattr(lc, "load_config", lambda k: str(doc_dir) if k == "doc_path" else "main")


@pytest.mark.e2e
class TestMainWindowStartup:
    def test_window_is_visible(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        win.show()
        assert win.isVisible()

    def test_docs_loaded(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        assert "svc_a" in win.docs
        assert "svc_b" in win.docs

    def test_doc_count(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        assert len(win.docs) == 2

    def test_scene_has_items(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        assert len(win.scene.items()) > 0

    def test_sidebar_exists(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        assert win.sidebar is not None

    def test_status_bar_exists(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        assert win.statusBar() is not None

    def test_edges_in_scene(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from line import Line
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        lines = [i for i in win.scene.items() if isinstance(i, Line)]
        assert len(lines) == 1
