from __future__ import annotations

import requests
from pytest_bdd import parsers, scenarios, when

from config.settings import Settings
from core.rest_client import given

scenarios("../../api/products_api.feature")


@when("I GET the products list")
def get_products_list(api_response: dict, api_client: requests.Session, settings: Settings) -> None:
    api_response["result"] = given(api_client, settings.api_base_url).when().get("/productsList")


@when(parsers.parse('I search for the product "{search_term}"'))
def search_product(
    api_response: dict, api_client: requests.Session, settings: Settings, search_term: str
) -> None:
    api_response["result"] = (
        given(api_client, settings.api_base_url)
        .form(search_product=search_term)
        .when()
        .post("/searchProduct")
    )
