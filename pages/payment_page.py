from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class PaymentPage(BasePage):
    """Encapsulates the /payment screen (dummy card details)."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.name_on_card_input = page.locator("[data-qa='name-on-card']")
        self.card_number_input = page.locator("[data-qa='card-number']")
        self.cvc_input = page.locator("[data-qa='cvc']")
        self.expiry_month_input = page.locator("[data-qa='expiry-month']")
        self.expiry_year_input = page.locator("[data-qa='expiry-year']")
        self.pay_button = page.locator("[data-qa='pay-button']")

    def pay_with_card(
        self,
        *,
        name_on_card: str,
        card_number: str,
        cvc: str,
        expiry_month: str,
        expiry_year: str,
    ) -> None:
        self.fill(self.name_on_card_input, name_on_card, name="name on card field")
        self.fill(self.card_number_input, card_number, name="card number field")
        self.fill(self.cvc_input, cvc, name="cvc field")
        self.fill(self.expiry_month_input, expiry_month, name="expiry month field")
        self.fill(self.expiry_year_input, expiry_year, name="expiry year field")
        self.click(self.pay_button, name="pay and confirm order button")
