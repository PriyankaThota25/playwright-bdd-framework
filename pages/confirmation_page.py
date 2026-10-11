from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class ConfirmationPage(BasePage):
    """Shared shape for the site's one-off confirmation screens (account
    created, order placed, account deleted), which all render a
    `[data-qa='<heading>']` message next to a `[data-qa='continue-button']`.
    """

    def __init__(self, page: Page, heading_data_qa: str):
        super().__init__(page)
        self.heading = page.locator(f"[data-qa='{heading_data_qa}']")
        self.continue_button = page.locator("[data-qa='continue-button']")

    def is_shown(self) -> bool:
        return self.is_visible(self.heading)

    def continue_to_home(self) -> None:
        self.click(self.continue_button, name="continue button")
