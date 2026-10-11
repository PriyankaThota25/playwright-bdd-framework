from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class CartPage(BasePage):
    """Encapsulates the /view_cart screen."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.checkout_button = page.locator("a:has-text('Proceed To Checkout')")
        self.first_remove_button = page.locator(".cart_quantity_delete").first
        self.empty_cart_message = page.locator("#empty_cart")

    def proceed_to_checkout(self) -> None:
        self.click(self.checkout_button, name="proceed to checkout button")

    def remove_first_product(self) -> None:
        self.click(self.first_remove_button, name="first product's remove button")

    def empty_cart_message_text(self) -> str:
        self.empty_cart_message.wait_for()
        return self.text_of(self.empty_cart_message, name="empty cart message")
