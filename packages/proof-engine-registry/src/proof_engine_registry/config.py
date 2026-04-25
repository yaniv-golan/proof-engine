"""Load registry configuration from ~/.config/proof-engine/registries.toml.

Tokens are never stored in the config file — only the NAME of the env var
that holds the token.
"""

from __future__ import annotations

import os
import tomllib
from dataclasses import dataclass, field
from pathlib import Path
from typing import Optional


class DuplicatePublishError(Exception):
    """More than one registry configured with publish = true."""


@dataclass(frozen=True)
class Registry:
    name: str
    url: str
    token: Optional[str] = None
    publish: bool = False
    fallback: bool = False  # implicit fallback from prior registry


def default_config_path() -> Path:
    xdg = os.environ.get("XDG_CONFIG_HOME")
    base = Path(xdg) if xdg else Path.home() / ".config"
    return base / "proof-engine" / "registries.toml"


def load_registries() -> list[Registry]:
    return load_registries_from_path(default_config_path())


def load_registries_from_path(path: Path) -> list[Registry]:
    if not path.exists():
        return []
    data = tomllib.loads(path.read_text())
    raw_list = data.get("registry", [])
    regs: list[Registry] = []
    for raw in raw_list:
        token = None
        if "token_env" in raw:
            env_name = raw["token_env"]
            token = os.environ.get(env_name)
            if token is None:
                raise RuntimeError(
                    f"Registry {raw.get('name', '?')!r} expects env var "
                    f"{env_name!r} but it is not set."
                )
        regs.append(Registry(
            name=raw["name"],
            url=raw["url"].rstrip("/"),
            token=token,
            publish=bool(raw.get("publish", False)),
            fallback=bool(raw.get("fallback", False)),
        ))
    publish_targets = [r for r in regs if r.publish]
    if len(publish_targets) > 1:
        raise DuplicatePublishError(
            f"Multiple publish targets configured: "
            f"{[r.name for r in publish_targets]}"
        )
    return regs
