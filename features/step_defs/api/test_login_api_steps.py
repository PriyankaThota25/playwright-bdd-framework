from __future__ import annotations

import requests
from pytest_bdd import parsers, scenarios, when

from config.settings import Settings
from core.rest_client import given

scenarios("../../api/login_api.feature")


@when(parsers.parse('I verify login as "{user_key}"'))
def verify_login(
    api_response: dict, api_client: requests.Session, settings: Settings, user_key: str
) -> None:
    credentials = settings.user(user_key)
    api_response["result"] = (
        given(api_client, settings.api_base_url)
        .form(email=credentials["email"], password=credentials["password"])
        .when()
        .post("/verifyLogin")
    )


@when("I verify login without credentials")
def verify_login_without_credentials(
    api_response: dict, api_client: requests.Session, settings: Settings
) -> None:
    api_response["result"] = given(api_client, settings.api_base_url).when().post("/verifyLogin")
