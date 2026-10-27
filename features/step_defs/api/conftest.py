from __future__ import annotations

import pytest
from pytest_bdd import parsers, then

from core.rest_client import ThenStep

# Fixtures and steps shared by every API feature live here, same convention
# as features/step_defs/conftest.py for the UI steps. Steps specific to one
# feature stay in that feature's own test_<feature>_steps.py.


@pytest.fixture
def api_response() -> dict:
    """Shared slot for the ThenStep produced by a @when step, read back by
    the generic @then assertions below."""
    return {}


@then(parsers.parse("the response status code should be {expected:d}"))
def assert_status_code(api_response: dict, expected: int) -> None:
    result: ThenStep = api_response["result"]
    result.status_code(expected)


@then(parsers.parse('the response field "{field}" should be {expected}'))
def assert_response_field(api_response: dict, field: str, expected: str) -> None:
    # Gherkin gives us plain text: "200" for numeric fields, '"User exists!"'
    # (quotes included) for string ones - coerce each to the right type.
    value: object
    if expected.isdigit():
        value = int(expected)
    else:
        value = expected.strip('"')
    result: ThenStep = api_response["result"]
    result.json_path(field, value)


@then("the response should contain at least 1 product")
def assert_has_products(api_response: dict) -> None:
    result: ThenStep = api_response["result"]
    products = result.extract("products")
    assert isinstance(products, list) and len(products) >= 1, (
        f"Expected at least one product in the response, got {products!r}"
    )
