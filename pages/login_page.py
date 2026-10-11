from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class LoginPage(BasePage):
    """Encapsulates every locator and interaction on the /login screen."""

    def __init__(self, page: Page):
        super().__init__(page)
        login_form = page.locator("form[action='/login']")
        self.email_input = login_form.locator("[data-qa='login-email']")
        self.password_input = login_form.locator("[data-qa='login-password']")
        self.login_button = login_form.locator("[data-qa='login-button']")
        self.error_banner = login_form.locator("p")

    def open(self) -> "LoginPage":
        self.goto("/login")
        return self

    def login(self, email: str, password: str) -> None:
        self.fill(self.email_input, email, name="email field")
        self.fill(self.password_input, password, name="password field")
        self.click(self.login_button, name="login button")

    def error_message(self) -> str:
        return self.text_of(self.error_banner, name="login error banner")
