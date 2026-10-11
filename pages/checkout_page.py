from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CheckoutPage(BasePage):
    """Encapsulates the /checkout screen (address + order review)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.place_order_button = page.locator("a:has-text('Place Order')")

    def place_order(self) -> None:
        self.click(self.place_order_button, name="place order button")
