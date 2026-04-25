import os
from pathlib import Path

import pytest

from proof_engine_registry.config import (
    Registry, load_registries, load_registries_from_path,
    DuplicatePublishError,
)


def _write_config(tmp_path: Path, body: str) -> Path:
    p = tmp_path / "registries.toml"
    p.write_text(body)
    return p


def test_loads_single_public_registry(tmp_path):
    path = _write_config(tmp_path, """
[[registry]]
name = "public"
url = "https://proofengine.info"
""")
    regs = load_registries_from_path(path)
    assert len(regs) == 1
    assert regs[0].name == "public"
    assert regs[0].url == "https://proofengine.info"
    assert regs[0].publish is False
    assert regs[0].token is None


def test_loads_token_from_env(tmp_path, monkeypatch):
    monkeypatch.setenv("MY_TOKEN", "s3cret")
    path = _write_config(tmp_path, """
[[registry]]
name = "private"
url = "https://p.example"
token_env = "MY_TOKEN"
""")
    regs = load_registries_from_path(path)
    assert regs[0].token == "s3cret"


def test_missing_token_env_is_error(tmp_path, monkeypatch):
    monkeypatch.delenv("MISSING_TOKEN", raising=False)
    path = _write_config(tmp_path, """
[[registry]]
name = "private"
url = "https://p.example"
token_env = "MISSING_TOKEN"
""")
    with pytest.raises(RuntimeError, match="MISSING_TOKEN"):
        load_registries_from_path(path)


def test_multiple_publish_targets_rejected(tmp_path):
    path = _write_config(tmp_path, """
[[registry]]
name = "a"
url = "https://a.example"
publish = true

[[registry]]
name = "b"
url = "https://b.example"
publish = true
""")
    with pytest.raises(DuplicatePublishError):
        load_registries_from_path(path)


def test_empty_config_returns_empty_list(tmp_path):
    path = _write_config(tmp_path, "")
    assert load_registries_from_path(path) == []


def test_missing_file_returns_empty_list(tmp_path):
    missing = tmp_path / "does-not-exist.toml"
    assert load_registries_from_path(missing) == []
