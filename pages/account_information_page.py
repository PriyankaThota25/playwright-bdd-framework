from __future__ import annotations

from playwright.sync_api import Page

from pages.base_page import BasePage


class AccountInformationPage(BasePage):
    """Encapsulates the "Enter Account Information" form on /signup."""

    def __init__(self, page: Page):
        super().__init__(page)
        self.title_mr_radio = page.locator("#id_gender1")
        self.password_input = page.locator("#password")
        self.dob_day_select = page.locator("#days")
        self.dob_month_select = page.locator("#months")
        self.dob_year_select = page.locator("#years")
        self.first_name_input = page.locator("#first_name")
        self.last_name_input = page.locator("#last_name")
        self.address_input = page.locator("#address1")
        self.country_select = page.locator("#country")
        self.state_input = page.locator("#state")
        self.city_input = page.locator("#city")
        self.zipcode_input = page.locator("#zipcode")
        self.mobile_number_input = page.locator("#mobile_number")
        self.create_account_button = page.locator("[data-qa='create-account']")

    def fill_account_details(
        self,
        *,
        password: str,
        first_name: str,
        last_name: str,
        address: str,
        country: str,
        state: str,
        city: str,
        zipcode: str,
        mobile_number: str,
    ) -> None:
        self.click(self.title_mr_radio, name="'Mr.' title radio button")
        self.fill(self.password_input, password, name="password field")
        self.dob_day_select.select_option("10")
        self.dob_month_select.select_option("5")
        self.dob_year_select.select_option("1990")
        self.fill(self.first_name_input, first_name, name="first name field")
        self.fill(self.last_name_input, last_name, name="last name field")
        self.fill(self.address_input, address, name="address field")
        self.country_select.select_option(country)
        self.fill(self.state_input, state, name="state field")
        self.fill(self.city_input, city, name="city field")
        self.fill(self.zipcode_input, zipcode, name="zipcode field")
        self.fill(self.mobile_number_input, mobile_number, name="mobile number field")
        self.click(self.create_account_button, name="create account button")
