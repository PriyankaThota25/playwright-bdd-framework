from __future__ import annotations

from playwright.sync_api import Locator, Page

from core.logger import get_logger

logger = get_logger(__name__)


class BasePage:
    def __init__(self, page: Page):
        self.page = page

    # --- navigation ---------------------------------------------------
    def goto(self, path: str = "/") -> None:
        logger.info("Navigating to %s", path)
        # Don't wait for the full 'load' event: the site's ads/third-party
        # resources can be slow and cause 30s timeouts.
        self.page.goto(path, wait_until="domcontentloaded")

    # --- actions --------------------------------------------------------
    def click(self, locator: Locator, *, name: str = "") -> None:
        logger.info("Clicking %s", name or locator)
        locator.click()

    def fill(self, locator: Locator, value: str, *, name: str = "") -> None:
        logger.info("Filling %s", name or locator)
        locator.fill(value)

    def text_of(self, locator: Locator, *, name: str = "") -> str:
        value = locator.inner_text()
        logger.debug("Read text of %s -> %r", name or locator, value)
        return value

    # --- state ------------------------------------------------------------
    def is_visible(self, locator: Locator) -> bool:
        return locator.is_visible()
    
    def set_input_files(self, locator: Locator, files: list[str]) -> None:
        logger.info("Setting input files for %s", locator)
        locator.set_input_files(files)