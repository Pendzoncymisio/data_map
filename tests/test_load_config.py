"""Unit tests for load_config.py — no Qt required."""

import json

import pytest

from load_config import load_config


@pytest.mark.unit
class TestLoadConfigDefaults:
    def test_doc_path_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert load_config("doc_path") == "../documentation/"

    def test_git_branch_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        assert load_config("git_branch_name") == "main"

    def test_unknown_key_raises_key_error(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        with pytest.raises(KeyError):
            load_config("nonexistent_key")


@pytest.mark.unit
class TestLoadConfigCustomFile:
    def test_custom_doc_path_overrides_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.json").write_text(json.dumps({"doc_path": "/custom/path/"}))
        assert load_config("doc_path") == "/custom/path/"

    def test_custom_branch_overrides_default(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.json").write_text(json.dumps({"git_branch_name": "develop"}))
        assert load_config("git_branch_name") == "develop"

    def test_partial_override_keeps_other_defaults(self, tmp_path, monkeypatch):
        """Specifying one key in config.json still returns defaults for others."""
        monkeypatch.chdir(tmp_path)
        (tmp_path / "config.json").write_text(json.dumps({"doc_path": "./custom/"}))
        assert load_config("git_branch_name") == "main"

    def test_extra_custom_key_is_accessible(self, tmp_path, monkeypatch):
        """Keys beyond the defaults are merged and accessible."""
        monkeypatch.chdir(tmp_path)
        cfg = {"doc_path": "./docs/", "extra_key": "extra_value"}
        (tmp_path / "config.json").write_text(json.dumps(cfg))
        assert load_config("extra_key") == "extra_value"

    def test_multiple_custom_keys(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        cfg = {"doc_path": "./docs/", "git_branch_name": "feature/x"}
        (tmp_path / "config.json").write_text(json.dumps(cfg))
        assert load_config("doc_path") == "./docs/"
        assert load_config("git_branch_name") == "feature/x"

    def test_no_config_file_does_not_raise(self, tmp_path, monkeypatch):
        monkeypatch.chdir(tmp_path)
        # Both default keys should be accessible without a config.json
        assert load_config("doc_path") is not None
        assert load_config("git_branch_name") is not None
