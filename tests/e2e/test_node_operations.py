"""E2E tests: node selection, sidebar updates, id change, delete."""

import json

import pytest


def _make_doc_dir(tmp_path):
    d = tmp_path / "docs"
    d.mkdir()
    data = {
        "alpha": {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}},
        "beta": {"icon": "default_icon.png", "viz": {"x": 200, "y": 0}, "sources": ["alpha"]},
        "gamma": {"icon": "default_icon.png", "viz": {"x": 100, "y": 200}},
    }
    (d / "main.json").write_text(json.dumps(data))
    return d


def _patch(monkeypatch, doc_dir):
    import load_config as lc
    import load_documentation as ld

    patch = lambda k: str(doc_dir) if k == "doc_path" else "main"  # noqa: E731
    monkeypatch.setattr(lc, "load_config", patch)
    monkeypatch.setattr(ld, "load_config", patch)


def _win(qtbot, tmp_path, monkeypatch):
    doc_dir = _make_doc_dir(tmp_path)
    _patch(monkeypatch, doc_dir)
    from main_window import MainWindow

    win = MainWindow()
    qtbot.addWidget(win)
    win.load_documentation_wrapper()
    return win


@pytest.mark.e2e
class TestNodeSelection:
    def test_click_sets_active_obj(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["alpha"]
        node.select_square()
        assert win.active_obj is node

    def test_click_populates_id_line(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["alpha"]
        node.select_square()
        assert win.sidebar.id_line.toPlainText() == "alpha"

    def test_click_populates_payload(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["alpha"]
        node.select_square()
        text = win.sidebar.text_area.toPlainText()
        assert "icon" in text

    def test_deselect_clears_active_obj(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["alpha"]
        node.select_square()
        assert win.active_obj is node
        node.deselect_square()
        assert win.active_obj is None

    def test_select_different_node_updates_active(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        win.docs["alpha"].select_square()
        win.docs["beta"].select_square()
        assert win.active_obj is win.docs["beta"]


@pytest.mark.e2e
class TestChangeId:
    def test_change_id_renames_key(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["gamma"]
        node.select_square()
        win.sidebar.id_line.setPlainText("gamma_renamed")
        win.change_id_wrapper()
        assert "gamma_renamed" in win.docs
        assert "gamma" not in win.docs

    def test_change_id_updates_node_id(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["gamma"]
        node.select_square()
        win.sidebar.id_line.setPlainText("gamma_v2")
        win.change_id_wrapper()
        assert win.docs["gamma_v2"].id == "gamma_v2"

    def test_change_id_to_existing_key_rejected(self, qtbot, tmp_path, monkeypatch):
        """Renaming to an already-existing id must not corrupt the docs dict."""
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["gamma"]
        node.select_square()
        win.sidebar.id_line.setPlainText("alpha")  # alpha already exists
        win.change_id_wrapper()
        # Both original keys must still be present
        assert "gamma" in win.docs
        assert "alpha" in win.docs


@pytest.mark.e2e
class TestDeleteViaMenu:
    def test_delete_removes_node(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["gamma"]
        node.select_square()
        node.delete()
        assert "gamma" not in win.docs

    def test_delete_removes_connected_line(self, qtbot, tmp_path, monkeypatch):
        from line import Line

        win = _win(qtbot, tmp_path, monkeypatch)
        lines_before = [i for i in win.scene.items() if isinstance(i, Line)]
        win.docs["alpha"].select_square()
        win.docs["alpha"].delete()
        lines_after = [i for i in win.scene.items() if isinstance(i, Line)]
        assert len(lines_after) < len(lines_before)

    def test_delete_removes_from_scene(self, qtbot, tmp_path, monkeypatch):
        win = _win(qtbot, tmp_path, monkeypatch)
        node = win.docs["gamma"]
        node.select_square()
        node.delete()
        assert node not in win.scene.items()


@pytest.mark.e2e
class TestSaveDocumentation:
    def test_save_writes_files(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        win.load_documentation_wrapper()
        win.save_documentation_wrapper()
        files = list(doc_dir.rglob("*.json"))
        assert len(files) >= 1

    def test_save_and_reload_preserves_nodes(self, qtbot, tmp_path, monkeypatch):
        doc_dir = _make_doc_dir(tmp_path)
        _patch(monkeypatch, doc_dir)
        from main_window import MainWindow

        win = MainWindow()
        qtbot.addWidget(win)
        win.load_documentation_wrapper()
        win.save_documentation_wrapper()

        _patch(monkeypatch, doc_dir)
        win2 = MainWindow()
        qtbot.addWidget(win2)
        win2.load_documentation_wrapper()
        assert set(win2.docs.keys()) == set(win.docs.keys())
