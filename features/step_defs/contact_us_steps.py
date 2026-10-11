from __future__ import annotations

import uuid

import pytest
from playwright.sync_api import Page
from pytest_bdd import parsers, scenarios, then, when

from pages.contact_us_page import ContactUsPage

scenarios("../contact_us.feature")

@pytest.fixture
def contact_us_page(page: Page) -> ContactUsPage:
    return ContactUsPage(page)

@when("I open the contact us page")
def open_contact_us_page(contact_us_page: ContactUsPage) -> None:
    contact_us_page.open_contact_us()

@when(parsers.parse('I fill the contact form with name "{name}", email "{email}", subject "{subject}" and message "{message}"'))
def fill_contact_form(contact_us_page: ContactUsPage, name: str, email: str, subject: str, message: str) -> None:
    contact_us_page.fill_contact_form(name, email, subject, message)

@when(parsers.parse('I attach the file "{file_path}"'))
def attach_file(contact_us_page: ContactUsPage, file_path: str) -> None:
    contact_us_page.attach_file(file_path)

@when("I submit the contact form")
def submit_contact_form(contact_us_page: ContactUsPage) -> None:
    contact_us_page.accept_alert()
    contact_us_page.submit_form()   

@then(parsers.parse('I should see the success message "{expected_message}"'))
def verify_success_message(contact_us_page: ContactUsPage, expected_message: str) -> None:
    actual_message = contact_us_page.get_success_message()
    assert actual_message == expected_message, f"Expected success message '{expected_message}', but got '{actual_message}'"     
