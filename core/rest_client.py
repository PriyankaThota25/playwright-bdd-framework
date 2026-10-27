from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import requests

# A small REST-Assured-style DSL for API testing, built on `requests`.
#
# Java:   given().baseUri(url).when().get("/users/1").then().statusCode(200);
# Here:   given(session, url).when().get("/users/1").status_code(200)
#
# `given()` returns a RequestSpec you configure (headers/params/body), whose
# `.when()` sends the request and returns a ThenStep you assert against.
# Every assertion method returns `self` so checks can be chained.


class ThenStep:
    """The response half of the chain. Holds the raw `requests.Response`
    alongside parsed JSON (when the body is JSON) and timing, and exposes
    chainable assertions mirroring RestAssured's `.then()...`."""

    def __init__(self, response: requests.Response, elapsed_ms: float) -> None:
        self.response = response
        self.elapsed_ms = elapsed_ms
        try:
            self._json: Any = response.json()
        except ValueError:
            self._json = None

    def status_code(self, expected: int) -> ThenStep:
        actual = self.response.status_code
        assert actual == expected, (
            f"Expected HTTP status {expected} but got {actual}. Body: {self.response.text[:500]!r}"
        )
        return self

    def header(self, name: str, expected: str) -> ThenStep:
        actual = self.response.headers.get(name)
        assert actual == expected, f"Expected header {name!r}={expected!r} but got {actual!r}"
        return self

    def body_contains(self, text: str) -> ThenStep:
        assert text in self.response.text, f"Expected response body to contain {text!r}"
        return self

    def json_path(self, path: str, expected: Any) -> ThenStep:
        actual = _extract(self._json, path)
        assert actual == expected, f"Expected '{path}' == {expected!r} but got {actual!r}"
        return self

    def json_path_contains(self, path: str, expected: Any) -> ThenStep:
        actual = _extract(self._json, path)
        assert expected in actual, f"Expected '{path}' to contain {expected!r}, got {actual!r}"
        return self

    def response_time_under(self, max_ms: float) -> ThenStep:
        assert self.elapsed_ms <= max_ms, (
            f"Expected response under {max_ms}ms, took {self.elapsed_ms:.0f}ms"
        )
        return self

    def extract(self, path: str | None = None) -> Any:
        """Pull a value out of the JSON body for use in a later request
        (e.g. chaining a created resource's id into the next call)."""
        return self._json if path is None else _extract(self._json, path)


def _extract(data: Any, path: str) -> Any:
    """Dotted-path lookup into parsed JSON, e.g. "products.0.name"."""
    current = data
    for part in path.split("."):
        if isinstance(current, list):
            current = current[int(part)]
        else:
            current = current[part]
    return current


class WhenStep:
    """The action half of the chain: fires the HTTP call configured by the
    RequestSpec and hands back a ThenStep to assert on."""

    def __init__(self, spec: RequestSpec) -> None:
        self._spec = spec

    def _send(self, method: str, endpoint: str) -> ThenStep:
        url = f"{self._spec.base_url.rstrip('/')}/{endpoint.lstrip('/')}"
        start = time.monotonic()
        response = self._spec.session.request(
            method,
            url,
            headers=self._spec.headers or None,
            params=self._spec.params or None,
            data=self._spec.form_data,
            json=self._spec.json_body,
            timeout=self._spec.timeout,
        )
        elapsed_ms = (time.monotonic() - start) * 1000
        return ThenStep(response, elapsed_ms)

    def get(self, endpoint: str) -> ThenStep:
        return self._send("GET", endpoint)

    def post(self, endpoint: str) -> ThenStep:
        return self._send("POST", endpoint)

    def put(self, endpoint: str) -> ThenStep:
        return self._send("PUT", endpoint)

    def delete(self, endpoint: str) -> ThenStep:
        return self._send("DELETE", endpoint)

    def patch(self, endpoint: str) -> ThenStep:
        return self._send("PATCH", endpoint)


@dataclass
class RequestSpec:
    """The request half of the chain. Configure it fluently, then call
    `.when()` to send it."""

    session: requests.Session
    base_url: str
    headers: dict[str, str] = field(default_factory=dict)
    params: dict[str, Any] = field(default_factory=dict)
    form_data: dict[str, Any] | None = None
    json_body: Any = None
    timeout: int = 10

    def header(self, name: str, value: str) -> RequestSpec:
        self.headers[name] = value
        return self

    def param(self, name: str, value: Any) -> RequestSpec:
        self.params[name] = value
        return self

    def form(self, **fields: Any) -> RequestSpec:
        self.form_data = {**(self.form_data or {}), **fields}
        return self

    def json(self, body: Any) -> RequestSpec:
        self.json_body = body
        return self

    def when(self) -> WhenStep:
        return WhenStep(self)


def given(session: requests.Session, base_url: str, timeout: int = 10) -> RequestSpec:
    """Entry point of the chain, e.g.:

        given(api_client, settings.api_base_url).form(email=..., password=...) \\
            .when().post("/verifyLogin") \\
            .status_code(200).json_path("message", "User exists!")
    """
    return RequestSpec(session=session, base_url=base_url, timeout=timeout)
