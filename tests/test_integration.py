"""Integration tests: load → save → reload round-trip."""

import pytest


def _patch(monkeypatch, doc_dir):
    import load_config as lc

    monkeypatch.setattr(lc, "load_config", lambda k: str(doc_dir) if k == "doc_path" else "main")


@pytest.mark.integration
class TestRoundTrip:
    def test_keys_preserved(self, qapp, simple_docs_dir, monkeypatch):
        _patch(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation
        from save_documentation import save_documentation

        docs = load_documentation()
        original_keys = set(docs.keys())
        for n in docs.values():
            n.setPos(n.rel_x, n.rel_y)
        save_documentation(docs)

        _patch(monkeypatch, simple_docs_dir)
        docs2 = load_documentation()
        assert set(docs2.keys()) == original_keys

    def test_icons_preserved(self, qapp, simple_docs_dir, monkeypatch):
        _patch(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation
        from save_documentation import save_documentation

        docs = load_documentation()
        for n in docs.values():
            n.setPos(n.rel_x, n.rel_y)
        save_documentation(docs)

        _patch(monkeypatch, simple_docs_dir)
        docs2 = load_documentation()
        for key, node in docs.items():
            assert docs2[key].payload.get("icon") == node.payload.get("icon")

    def test_source_links_preserved(self, qapp, simple_docs_dir, monkeypatch):
        _patch(monkeypatch, simple_docs_dir)
        from load_documentation import load_documentation
        from save_documentation import save_documentation

        docs = load_documentation()
        for n in docs.values():
            n.setPos(n.rel_x, n.rel_y)
        save_documentation(docs)

        _patch(monkeypatch, simple_docs_dir)
        docs2 = load_documentation()
        assert len(docs2["node_b"].inbound_lines) == 1
        assert docs2["node_b"].inbound_lines[0].source_doc is docs2["node_a"]

    def test_group_hierarchy_preserved(self, qapp, grouped_docs_dir, monkeypatch):
        _patch(monkeypatch, grouped_docs_dir)
        from load_documentation import load_documentation
        from save_documentation import save_documentation

        docs = load_documentation()
        for n in docs.values():
            n.setPos(n.pos().x(), n.pos().y())
        save_documentation(docs)

        _patch(monkeypatch, grouped_docs_dir)
        docs2 = load_documentation()
        assert docs2["group_1"].group is True
        assert len(docs2["group_1"].children_docs) == 2

    def test_multi_file_round_trip(self, qapp, multi_file_docs_dir, monkeypatch):
        _patch(monkeypatch, multi_file_docs_dir)
        from load_documentation import load_documentation
        from save_documentation import save_documentation

        docs = load_documentation()
        for n in docs.values():
            n.setPos(n.rel_x, n.rel_y)
        save_documentation(docs)

        # Verify two separate JSON files were written
        files = list(multi_file_docs_dir.rglob("*.json"))
        assert len(files) == 2

        _patch(monkeypatch, multi_file_docs_dir)
        docs2 = load_documentation()
        assert "node_x" in docs2
        assert "node_y" in docs2
