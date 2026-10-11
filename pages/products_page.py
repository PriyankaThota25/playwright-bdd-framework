from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class ProductsPage(BasePage):
    """Encapsulates the /products catalog: searching and adding to cart."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.search_input = page.locator("#search_product")
        self.search_button = page.locator("#submit_search")
        self.results_heading = page.locator(".features_items h2.title")
        self.first_add_to_cart_button = page.locator(".features_items .productinfo .add-to-cart"
        ).first
        self.view_cart_link = page.locator(".modal-content a:has-text('View Cart')")

    def open(self) -> "ProductsPage":
        self.goto("/products")
        return self

    def search(self, term: str) -> None:
        self.fill(self.search_input, term, name="product search field")
        self.click(self.search_button, name="product search button")

    def results_heading_text(self) -> str:
        return self.text_of(self.results_heading, name="search results heading")

    def add_first_result_to_cart(self) -> None:
        self.click(self.first_add_to_cart_button, name="first product's add-to-cart button")
        self.click(self.view_cart_link, name="view cart link")
