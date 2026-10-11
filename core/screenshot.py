from __future__ import annotations

import re
from datetime import datetime
from pathlib import Path

from playwright.sync_api import Page

SCREENSHOT_DIR = Path(__file__).parent.parent / "reports" / "screenshots"


def _slugify(name: str) -> str:
    slug = re.sub(r"[^\w\-]+", "_", name.strip())
    return slug.strip("_") or "scenario"


class ScenarioScreenshots:
    """Captures one screenshot per step into a folder scoped to a single scenario run."""

    def __init__(self, scenario_name: str):
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        base_name = f"{_slugify(scenario_name)}_{timestamp}"

        # Guarantee a fresh, never-shared folder: if a scenario folder with this
        # exact name already exists (e.g. two scenario-outline examples resolving
        # to the same microsecond, or parallel pytest-xdist workers), fall back to
        # a numbered suffix instead of silently reusing/merging into it.
        candidate = SCREENSHOT_DIR / base_name
        suffix = 1
        while True:
            try:
                candidate.mkdir(parents=True, exist_ok=False)
                break
            except FileExistsError:
                suffix += 1
                candidate = SCREENSHOT_DIR / f"{base_name}_{suffix}"

        self.dir = candidate
        self._step_count = 0

    def capture(self, page: Page, *, failed: bool = False) -> Path:
        self._step_count += 1
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S_%f")
        suffix = "_failed" if failed else ""
        path = self.dir / f"step{self._step_count}_{timestamp}{suffix}.png"
        page.screenshot(path=str(path))
        return path
