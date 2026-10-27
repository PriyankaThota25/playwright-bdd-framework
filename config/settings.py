from __future__ import annotations

import os
from dataclasses import dataclass, field
from functools import lru_cache
from pathlib import Path
from typing import Any

import yaml

CONFIG_DIR = Path(__file__).parent / "environments"


@dataclass(frozen=True)
class Viewport:
    width: int
    height: int


@dataclass(frozen=True)
class Settings:
    env_name: str
    base_url: str
    api_base_url: str
    browser: str
    headless: bool
    slow_mo: int
    viewport: Viewport
    timeout: int
    navigation_timeout: int
    credentials: dict[str, dict[str, str]] = field(default_factory=dict)

    def user(self, key: str) -> dict[str, str]:
        return self.credentials[key]


@lru_cache(maxsize=None)
def get_settings(env_name: str | None = None) -> Settings:
    env_name = env_name or os.getenv("TEST_ENV", "dev")
    config_path = CONFIG_DIR / f"{env_name}.yaml"
    if not config_path.exists():
        raise FileNotFoundError(f"No config file for '{env_name}' at {config_path}")

    with open(config_path, encoding="utf-8") as f:
        raw: dict[str, Any] = yaml.safe_load(f)

    return Settings(
        env_name=env_name,
        base_url=raw["base_url"],
        api_base_url=raw.get("api_base_url", f"{raw['base_url']}/api"),
        browser=raw["browser"],
        headless=raw["headless"],
        slow_mo=raw.get("slow_mo", 0),
        viewport=Viewport(**raw["viewport"]),
        timeout=raw.get("timeout", 10000),
        navigation_timeout=raw.get("navigation_timeout", 30000),
        credentials=raw.get("credentials", {}),
    )