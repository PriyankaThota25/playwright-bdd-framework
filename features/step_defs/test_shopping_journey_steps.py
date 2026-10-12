from __future__ import annotations

import pytest
from playwright.sync_api import Page
from pytest_bdd import parsers, scenarios, then, when

from pages.cart_page import CartPage
from pages.confirmation_page import ConfirmationPage
from pages.checkout_page import CheckoutPage
from pages.home_page import HomePage
from pages.payment_page import PaymentPage
from pages.products_page import ProductsPage

# "Given I am on the home page" and the home_page fixture live in conftest.py
# since they're reusable by other feature files. Only steps specific to
# shopping_journey.feature belong here.

scenarios("../shopping_journey.feature")


@pytest.fixture
def products_page(page: Page) -> ProductsPage:
    return ProductsPage(page)


@pytest.fixture
def cart_page(page: Page) -> CartPage:
    return CartPage(page)


@pytest.fixture
def checkout_page(page: Page) -> CheckoutPage:
    return CheckoutPage(page)


@pytest.fixture
def payment_page(page: Page) -> PaymentPage:
    return PaymentPage(page)


@when("I navigate to the products page")
def navigate_to_products_page(products_page: ProductsPage) -> None:
    products_page.open()


@when(parsers.parse('I search for "{term}" in the product catalog'))
def search_for_product(products_page: ProductsPage, term: str) -> None:
    products_page.search(term)


@then("I should see matching search results")
def assert_search_results_shown(products_page: ProductsPage) -> None:
    assert products_page.results_heading_text().strip().lower() == "searched products"


@when("I add the first search result to my cart")
def add_first_result_to_cart(products_page: ProductsPage) -> None:
    products_page.add_first_result_to_cart()


@when("I proceed to checkout")
def proceed_to_checkout(cart_page: CartPage) -> None:
    cart_page.proceed_to_checkout()


@when("I remove the product from my cart")
def remove_product_from_cart(cart_page: CartPage) -> None:
    cart_page.remove_first_product()


@then("I should see that my cart is empty")
def assert_cart_is_empty(cart_page: CartPage) -> None:
    assert "cart is empty" in cart_page.empty_cart_message_text().lower()


@when("I place the order with valid payment details")
def place_order_with_valid_payment_details(
    checkout_page: CheckoutPage, payment_page: PaymentPage, new_customer: dict
) -> None:
    checkout_page.place_order()
    payment_page.pay_with_card(
        name_on_card=new_customer["name"],
        card_number="4242424242424242",
        cvc="123",
        expiry_month="12",
        expiry_year="2028",
    )


@then("I should see my order confirmation")
def assert_order_confirmation(page: Page) -> None:
    assert ConfirmationPage(page, "order-placed").is_shown()
    ConfirmationPage(page, "order-placed").continue_to_home()


@when("I delete my account")
def delete_my_account(home_page: HomePage) -> None:
    home_page.delete_account()


@then("I should see my account deletion confirmation")
def assert_account_deletion_confirmation(page: Page) -> None:
    assert ConfirmationPage(page, "account-deleted").is_shown()
