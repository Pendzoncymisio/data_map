"""Unit tests for Line geometry (line.py) — requires Qt."""

import pytest
from PyQt6.QtCore import QPointF

from doc_obj import DocObj
from line import _CARD_SIZE, Line


def _node(id_="n", x=0, y=0):
    """Create a minimal DocObj positioned at (x, y)."""
    docs = {}
    n = DocObj(id_, {"icon": "default_icon.png", "viz": {"x": x, "y": y}}, docs, "t.json")
    n.setPos(x, y)
    return n


@pytest.mark.qt
class TestConnectorPoints:
    def test_horizontal_dominant_right(self, qapp):
        """src left of snk → right edge of src, left edge of snk."""
        src = _node("s", 0, 0)
        snk = _node("k", 200, 0)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        p1, p2 = line._connector_points()
        assert p1.x() == pytest.approx(_CARD_SIZE)
        assert p2.x() == pytest.approx(200)

    def test_horizontal_dominant_left(self, qapp):
        """src right of snk → left edge of src, right edge of snk."""
        src = _node("s", 200, 0)
        snk = _node("k", 0, 0)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        p1, p2 = line._connector_points()
        assert p1.x() == pytest.approx(200)
        assert p2.x() == pytest.approx(_CARD_SIZE)

    def test_vertical_dominant_down(self, qapp):
        """src above snk → bottom edge of src, top edge of snk."""
        src = _node("s", 0, 0)
        snk = _node("k", 0, 200)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        p1, p2 = line._connector_points()
        assert p1.y() == pytest.approx(_CARD_SIZE)
        assert p2.y() == pytest.approx(200)

    def test_vertical_dominant_up(self, qapp):
        """src below snk → top edge of src, bottom edge of snk."""
        src = _node("s", 0, 200)
        snk = _node("k", 0, 0)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        p1, p2 = line._connector_points()
        assert p1.y() == pytest.approx(200)
        assert p2.y() == pytest.approx(_CARD_SIZE)

    def test_centre_y_on_horizontal_connection(self, qapp):
        """Both connector points share the vertical centre of their nodes."""
        src = _node("s", 0, 0)
        snk = _node("k", 200, 0)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        p1, p2 = line._connector_points()
        assert p1.y() == pytest.approx(_CARD_SIZE / 2)
        assert p2.y() == pytest.approx(_CARD_SIZE / 2)


@pytest.mark.qt
class TestBuildPath:
    def _make_line(self, qapp, x1=0, y1=0, x2=100, y2=0):
        src = _node("s", x1, y1)
        snk = _node("k", x2, y2)
        line = Line.__new__(Line)
        line.source_doc = src
        line.sink_doc = snk
        return line

    def test_path_starts_near_p1(self, qapp):
        line = self._make_line(qapp)
        p1, p2 = QPointF(0, 0), QPointF(100, 0)
        path = line._build_path(p1, p2)
        start = path.pointAtPercent(0)
        assert start.x() == pytest.approx(p1.x(), abs=1)
        assert start.y() == pytest.approx(p1.y(), abs=1)

    def test_path_ends_near_p2(self, qapp):
        line = self._make_line(qapp)
        p1, p2 = QPointF(0, 0), QPointF(100, 0)
        path = line._build_path(p1, p2)
        end = path.pointAtPercent(1)
        assert end.x() == pytest.approx(p2.x(), abs=1)
        assert end.y() == pytest.approx(p2.y(), abs=1)

    def test_path_not_empty(self, qapp):
        line = self._make_line(qapp)
        path = line._build_path(QPointF(0, 0), QPointF(100, 50))
        assert not path.isEmpty()

    def test_vertical_path_not_empty(self, qapp):
        line = self._make_line(qapp, x2=0, y2=200)
        path = line._build_path(QPointF(0, 0), QPointF(0, 200))
        assert not path.isEmpty()


@pytest.mark.qt
class TestFullLineConstruction:
    def test_update_position_builds_path(self, qapp):
        src = _node("s", 0, 0)
        snk = _node("k", 200, 0)
        line = Line(src, snk)
        assert not line._path.isEmpty()

    def test_bounding_rect_padded(self, qapp):
        src = _node("s", 0, 0)
        snk = _node("k", 200, 0)
        line = Line(src, snk)
        path_rect = line._path.boundingRect()
        br = line.boundingRect()
        assert br.width() > path_rect.width()
        assert br.height() > path_rect.height()

    def test_bounding_rect_not_null(self, qapp):
        src = _node("s", 0, 0)
        snk = _node("k", 0, 200)
        line = Line(src, snk)
        assert not line.boundingRect().isNull()
