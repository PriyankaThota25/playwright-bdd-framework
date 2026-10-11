from __future__ import annotations

from pytest_bdd import parsers, scenarios, then, when

from config.settings import Settings
from pages.home_page import HomePage
from pages.login_page import LoginPage

# "Given I am on the login page" and the login_page/home_page fixtures
# live in conftest.py since they're reusable by other feature files. Only
# steps specific to login.feature belong here.

scenarios("../login.feature")


@when(parsers.parse('I log in as "{user_key}"'))
def log_in_as(login_page: LoginPage, settings: Settings, user_key: str) -> None:
    credentials = settings.user(user_key)
    login_page.login(credentials["email"], credentials["password"])


@then("I should be logged in successfully")
def assert_logged_in(home_page: HomePage) -> None:
    home_page.wait_until_logged_in()


@then("I should see an invalid credentials error")
def assert_invalid_credentials_error(login_page: LoginPage) -> None:
    assert login_page.error_message() == "Your email or password is incorrect!"
