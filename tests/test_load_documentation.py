"""Tests for load_documentation.py — requires Qt (QGraphicsItem creation)."""

import pytest

from load_documentation import get_files_to_open

# ---------------------------------------------------------------------------
# get_files_to_open — pure I/O, no Qt needed
# ---------------------------------------------------------------------------


@pytest.mark.unit
class TestGetFilesToOpen:
    def test_returns_json_files(self, tmp_path):
        (tmp_path / "a.json").write_text("{}")
        (tmp_path / "b.json").write_text("{}")
        result = get_files_to_open(str(tmp_path))
        assert len(result) == 2
        assert all(f.endswith(".json") for f in result)

    def test_ignores_non_json_files(self, tmp_path):
        (tmp_path / "a.json").write_text("{}")
        (tmp_path / "b.txt").write_text("ignored")
        (tmp_path / "c.yaml").write_text("ignored")
        result = get_files_to_open(str(tmp_path))
        assert len(result) == 1

    def test_recurses_into_subdirectories(self, tmp_path):
        sub = tmp_path / "sub"
        sub.mkdir()
        (tmp_path / "root.json").write_text("{}")
        (sub / "child.json").write_text("{}")
        result = get_files_to_open(str(tmp_path))
        assert len(result) == 2

    def test_empty_directory_returns_empty_list(self, tmp_path):
        assert get_files_to_open(str(tmp_path)) == []

    def test_deeply_nested_file_found(self, tmp_path):
        deep = tmp_path / "a" / "b" / "c"
        deep.mkdir(parents=True)
        (deep / "deep.json").write_text("{}")
        result = get_files_to_open(str(tmp_path))
        assert len(result) == 1
        assert result[0].endswith("deep.json")


# ---------------------------------------------------------------------------
# load_documentation — needs QApplication
# ---------------------------------------------------------------------------


def _patch_doc_path(monkeypatch, doc_dir):
    """Patch load_config so load_documentation uses the given tmp dir."""
    import load_config as lc
    import load_documentation as ld

    patch = lambda k: str(doc_dir) if k == "doc_path" else "main"  # noqa: E731
    monkeypatch.setattr(lc, "load_config", patch)
    monkeypatch.setattr(ld, "load_config", patch)


@pytest.mark.qt
class TestLoadDocumentation:
    def test_returns_all_nodes(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert "node_a" in result
        assert "node_b" in result

    def test_node_count(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert len(result) == 2

    def test_source_lines_wired(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        node_b = result["node_b"]
        assert len(node_b.inbound_lines) == 1
        assert node_b.inbound_lines[0].source_doc is result["node_a"]

    def test_outbound_line_on_source(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert len(result["node_a"].outbound_lines) == 1

    def test_group_is_set(self, qapp, grouped_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, grouped_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert result["group_1"].group is True

    def test_group_children_count(self, qapp, grouped_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, grouped_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert len(result["group_1"].children_docs) == 2

    def test_children_parent_doc_set(self, qapp, grouped_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, grouped_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert result["child_a"].parent_doc is result["group_1"]
        assert result["child_b"].parent_doc is result["group_1"]

    def test_root_nodes_have_no_parent(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        roots = [n for n in result.values() if n.parent_doc is None]
        assert len(roots) == 2  # both nodes are root level

    def test_multi_file_documentation(self, qapp, multi_file_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, multi_file_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert "node_x" in result
        assert "node_y" in result

    def test_leaf_nodes_are_not_groups(self, qapp, simple_docs_dir, monkeypatch):
        _patch_doc_path(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation

        result = load_documentation()
        assert result["node_a"].group is False
        assert result["node_b"].group is False
