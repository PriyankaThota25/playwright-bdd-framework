from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """Encapsulates the /view_cart screen."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.checkout_button = page.locator("a:has-text('Proceed To Checkout')")

    def proceed_to_checkout(self) -> None:
        self.click(self.checkout_button, name="proceed to checkout button")
