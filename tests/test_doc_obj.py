"""Unit tests for DocObj (doc_obj.py) — requires Qt."""

import pytest

from doc_obj import LABEL_W, TOTAL_H, DocObj
from line import Line


def _node(id_="n", x=0, y=0, docs=None):
    if docs is None:
        docs = {}
    n = DocObj(id_, {"icon": "default_icon.png", "viz": {"x": x, "y": y}}, docs, "test.json")
    return n


@pytest.mark.qt
class TestBoundingRect:
    def test_leaf_node_width(self, qapp):
        assert _node().boundingRect().width() == LABEL_W

    def test_leaf_node_height(self, qapp):
        assert _node().boundingRect().height() == TOTAL_H

    def test_group_uses_wh(self, qapp):
        n = _node()
        n.group = True
        n.w, n.h = 300, 200
        r = n.boundingRect()
        assert r.width() == 300
        assert r.height() == 200


@pytest.mark.qt
class TestPositionHelpers:
    def test_rel_to_abs_no_parent(self, qapp):
        n = _node(x=42, y=17)
        assert n.position_rel_to_abs() == {"x": 42, "y": 17}

    def test_rel_to_abs_with_parent(self, qapp):
        docs = {}
        parent = _node("p", 10, 20, docs)
        child = _node("c", 5, 8, docs)
        child.parent_doc = parent
        pos = child.position_rel_to_abs({"x": 10, "y": 20})
        assert pos == {"x": 15, "y": 28}

    def test_abs_to_rel_no_parent(self, qapp):
        n = _node()
        n.setPos(60, 40)  # 20px-grid-aligned so itemChange snap is a no-op
        assert n.position_abs_to_rel() == {"x": 60, "y": 40}

    def test_abs_to_rel_with_parent(self, qapp):
        docs = {}
        parent = _node("p", 0, 0, docs)
        child = _node("c", 0, 0, docs)
        parent.setPos(100, 40)  # 20px-grid-aligned
        child.setPos(160, 80)  # 20px-grid-aligned
        child.parent_doc = parent
        pos = child.position_abs_to_rel()
        assert pos == {"x": 60, "y": 40}


@pytest.mark.qt
class TestChildManagement:
    def test_add_child(self, qapp):
        docs = {}
        parent = _node("p", docs=docs)
        child = _node("c", docs=docs)
        parent.add_child_document(child)
        assert child in parent.children_docs

    def test_remove_child(self, qapp):
        docs = {}
        parent = _node("p", docs=docs)
        child = _node("c", docs=docs)
        parent.add_child_document(child)
        parent.remove_child_document(child)
        assert child not in parent.children_docs

    def test_multiple_children(self, qapp):
        docs = {}
        parent = _node("p", docs=docs)
        c1 = _node("c1", docs=docs)
        c2 = _node("c2", docs=docs)
        parent.add_child_document(c1)
        parent.add_child_document(c2)
        assert len(parent.children_docs) == 2


@pytest.mark.qt
class TestSourcesSinks:
    def test_get_sources(self, qapp):
        docs = {}
        src = _node("src", docs=docs)
        snk = _node("snk", docs=docs)
        line = Line(src, snk)
        src.outbound_lines.append(line)
        snk.inbound_lines.append(line)
        assert snk.get_sources() == [src]

    def test_get_sinks(self, qapp):
        docs = {}
        src = _node("src", docs=docs)
        snk = _node("snk", docs=docs)
        line = Line(src, snk)
        src.outbound_lines.append(line)
        snk.inbound_lines.append(line)
        assert src.get_sinks() == [snk]

    def test_empty_sources(self, qapp):
        assert _node().get_sources() == []

    def test_empty_sinks(self, qapp):
        assert _node().get_sinks() == []

    def test_multiple_sources(self, qapp):
        docs = {}
        s1 = _node("s1", docs=docs)
        s2 = _node("s2", docs=docs)
        snk = _node("snk", docs=docs)
        for src in (s1, s2):
            line = Line(src, snk)
            src.outbound_lines.append(line)
            snk.inbound_lines.append(line)
        assert set(snk.get_sources()) == {s1, s2}


@pytest.mark.qt
class TestMakeGroupFinal:
    def test_make_group_sets_flag(self, qapp):
        n = _node()
        n.make_group()
        assert n.group is True

    def test_make_final_clears_group(self, qapp):
        n = _node()
        n.make_group()
        n.make_final()
        assert n.group is False

    def test_make_final_sets_z_value(self, qapp):
        n = _node()
        n.make_final()
        assert n.zValue() == 99

    def test_make_group_then_expandable_false(self, qapp):
        n = _node()
        n.make_group()
        assert n.expandable is False


@pytest.mark.qt
class TestDeleteNode:
    def test_delete_removes_from_docs_dict(self, qapp, scene_view):
        scene, view, _ = scene_view
        docs = {}
        n = _node("victim", docs=docs)
        scene.addItem(n)
        n.delete()
        assert "victim" not in docs

    def test_delete_removes_from_scene(self, qapp, scene_view):
        scene, view, _ = scene_view
        docs = {}
        n = _node("victim", docs=docs)
        scene.addItem(n)
        n.delete()
        assert n not in scene.items()

    def test_delete_cleans_outbound_lines(self, qapp, scene_view):
        scene, view, _ = scene_view
        docs = {}
        src = _node("src", docs=docs)
        snk = _node("snk", docs=docs)
        scene.addItem(src)
        scene.addItem(snk)
        line = Line(src, snk)
        src.outbound_lines.append(line)
        snk.inbound_lines.append(line)
        scene.addItem(line)

        snk.delete()

        assert len(src.outbound_lines) == 0
        assert line not in scene.items()

    def test_delete_cleans_inbound_lines(self, qapp, scene_view):
        scene, view, _ = scene_view
        docs = {}
        src = _node("src", docs=docs)
        snk = _node("snk", docs=docs)
        scene.addItem(src)
        scene.addItem(snk)
        line = Line(src, snk)
        src.outbound_lines.append(line)
        snk.inbound_lines.append(line)
        scene.addItem(line)

        src.delete()

        assert len(snk.inbound_lines) == 0


@pytest.mark.qt
class TestCollapseExpand:
    def _setup(self, scene):
        docs = {}
        parent = _node("par", docs=docs)
        child = _node("chi", docs=docs)
        parent.group = True
        parent.add_child_document(child)
        child.parent_doc = parent
        parent.setPos(0, 0)
        child.setPos(20, 20)
        scene.addItem(parent)
        scene.addItem(child)
        return parent, child

    def test_collapse_sets_expandable(self, qapp, scene_view):
        scene, view, _ = scene_view
        parent, _ = self._setup(scene)
        parent.collapse()
        assert parent.expandable is True

    def test_collapse_hides_child(self, qapp, scene_view):
        scene, view, _ = scene_view
        parent, child = self._setup(scene)
        parent.collapse()
        assert not child.isVisible()

    def test_expand_noop_when_not_expandable(self, qapp, scene_view):
        scene, view, _ = scene_view
        parent, _ = self._setup(scene)
        parent.expandable = False
        parent.expand()  # should be a no-op
        assert parent.expandable is False

    def test_collapse_then_expand_restores_visibility(self, qapp, scene_view):
        scene, view, _ = scene_view
        parent, child = self._setup(scene)
        parent.collapse()
        assert not child.isVisible()
        parent.expand()
        assert child.isVisible()

    def test_expand_clears_expandable(self, qapp, scene_view):
        scene, view, _ = scene_view
        parent, child = self._setup(scene)
        parent.collapse()
        parent.expand()
        assert parent.expandable is False


@pytest.mark.qt
class TestOpenInBrowser:
    def test_no_link_does_not_raise(self, qapp):
        n = _node()
        n.open_in_browser()  # payload has no link — should just print

    def test_with_link_calls_browser(self, qapp, monkeypatch):
        import webbrowser

        calls = []
        monkeypatch.setattr(webbrowser, "open", lambda url: calls.append(url))
        docs = {}
        n = DocObj(
            "linked",
            {"icon": "default_icon.png", "viz": {"x": 0, "y": 0}, "link": "https://example.com"},
            docs,
            "test.json",
        )
        n.open_in_browser()
        assert calls == ["https://example.com"]
