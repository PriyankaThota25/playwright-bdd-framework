from __future__ import annotations

import re

from playwright.sync_api import Page, expect

from pages.base_page import BasePage


class HomePage(BasePage):
    """Encapsulates every locator and interaction on the / (home) screen."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.logged_in_indicator = page.locator("a:has-text('Logged in as')")
        self.logged_in_username = self.logged_in_indicator.locator("b")
        self.logout_link = page.locator("a[href='/logout']")
        self.delete_account_link = page.locator("a[href='/delete_account']")

    def open(self) -> "HomePage":
        self.goto("/")
        return self

    def delete_account(self) -> None:
        self.click(self.delete_account_link, name="delete account link")

    def wait_until_logged_in(self) -> None:
        expect(self.page).to_have_url(re.compile(r"/$"))
        expect(self.logged_in_indicator).to_be_visible()

    def username(self) -> str:
        return self.text_of(self.logged_in_username, name="logged-in username")
