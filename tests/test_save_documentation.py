"""Unit tests for save_documentation.py — no Qt required."""

import json
import os
from unittest.mock import MagicMock

import pytest

from save_documentation import save_documentation


def _mock_obj(id_, payload, source_file, pos_x=0, pos_y=0):
    obj = MagicMock()
    obj.id = id_
    obj.payload = dict(payload)
    obj.source_file = source_file
    obj.position_abs_to_rel.return_value = {"x": pos_x, "y": pos_y}
    return obj


@pytest.mark.unit
class TestSaveCreatesFiles:
    def test_creates_output_file(self, tmp_path):
        src = str(tmp_path / "out.json")
        save_documentation({"n": _mock_obj("n", {}, src)})
        assert os.path.exists(src)

    def test_creates_missing_directories(self, tmp_path):
        nested = str(tmp_path / "a" / "b" / "c" / "out.json")
        save_documentation({"n": _mock_obj("n", {}, nested)})
        assert os.path.exists(nested)

    def test_output_is_valid_json(self, tmp_path):
        src = str(tmp_path / "out.json")
        save_documentation({"n": _mock_obj("n", {"icon": "x.png"}, src)})
        with open(src) as f:
            data = json.load(f)
        assert isinstance(data, dict)


@pytest.mark.unit
class TestSavePayload:
    def test_node_id_present_in_output(self, tmp_path):
        src = str(tmp_path / "out.json")
        save_documentation({"my_node": _mock_obj("my_node", {}, src)})
        with open(src) as f:
            data = json.load(f)
        assert "my_node" in data

    def test_payload_fields_preserved(self, tmp_path):
        src = str(tmp_path / "out.json")
        payload = {"icon": "test.png", "link": "https://example.com"}
        save_documentation({"n": _mock_obj("n", payload, src)})
        with open(src) as f:
            data = json.load(f)
        assert data["n"]["icon"] == "test.png"
        assert data["n"]["link"] == "https://example.com"

    def test_viz_written_from_position(self, tmp_path):
        src = str(tmp_path / "out.json")
        save_documentation({"n": _mock_obj("n", {}, src, pos_x=42, pos_y=77)})
        with open(src) as f:
            data = json.load(f)
        assert data["n"]["viz"] == {"x": 42, "y": 77}

    def test_multiple_nodes_in_one_file(self, tmp_path):
        src = str(tmp_path / "out.json")
        docs = {
            "n1": _mock_obj("n1", {"v": 1}, src),
            "n2": _mock_obj("n2", {"v": 2}, src),
            "n3": _mock_obj("n3", {"v": 3}, src),
        }
        save_documentation(docs)
        with open(src) as f:
            data = json.load(f)
        assert len(data) == 3
        assert data["n1"]["v"] == 1
        assert data["n3"]["v"] == 3


@pytest.mark.unit
class TestSaveGroupsBySourceFile:
    def test_nodes_split_across_files(self, tmp_path):
        src_a = str(tmp_path / "a.json")
        src_b = str(tmp_path / "b.json")
        docs = {
            "na": _mock_obj("na", {}, src_a),
            "nb": _mock_obj("nb", {}, src_b),
            "nc": _mock_obj("nc", {}, src_a),
        }
        save_documentation(docs)
        with open(src_a) as f:
            data_a = json.load(f)
        with open(src_b) as f:
            data_b = json.load(f)
        assert "na" in data_a
        assert "nc" in data_a
        assert "nb" not in data_a
        assert "nb" in data_b

    def test_empty_dict_produces_no_files(self, tmp_path):
        save_documentation({})
        assert list(tmp_path.iterdir()) == []
