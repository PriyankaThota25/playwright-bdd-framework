from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class SignupPage(BasePage):
    """Encapsulates the "New User Signup!" mini-form on the /login screen."""

    def __init__(self, page: Page):
        super().__init__(page)
        signup_form = page.locator("form[action='/signup']")
        self.name_input = signup_form.locator("[data-qa='signup-name']")
        self.email_input = signup_form.locator("[data-qa='signup-email']")
        self.signup_button = signup_form.locator("[data-qa='signup-button']")

    def open(self) -> "SignupPage":
        self.goto("/login")
        return self

    def start_signup(self, name: str, email: str) -> None:
        self.fill(self.name_input, name, name="signup name field")
        self.fill(self.email_input, email, name="signup email field")
        self.click(self.signup_button, name="signup button")
