"""Synchronous client for the hosted UnifyUnits Measurement API."""

from __future__ import annotations

from typing import Any, Mapping, Sequence
from urllib.parse import quote

import httpx


class ApiError(httpx.HTTPStatusError):
    """An HTTP error returned by the API, with structured error helpers."""

    def __init__(self, error: httpx.HTTPStatusError) -> None:
        super().__init__(str(error), request=error.request, response=error.response)

    @property
    def error(self) -> Mapping[str, Any]:
        value = self.response.json().get("error", {})
        return value if isinstance(value, dict) else {}

    @property
    def error_code(self) -> str | None:
        return self.error.get("code")

    @property
    def request_id(self) -> str | None:
        return self.error.get("request_id") or self.response.headers.get("X-Request-Id")

    @property
    def details(self) -> Mapping[str, Any] | None:
        return self.error.get("details")


class UnifyUnits:
    """Client for conversions and public unit catalog endpoints.

    Values are strings to preserve decimal precision. Supply an API key for
    conversion endpoints; catalog and health endpoints are public.
    """

    def __init__(
        self,
        api_key: str | None = None,
        *,
        base_url: str = "https://api.unifyunits.com",
        timeout: float = 10.0,
        transport: httpx.BaseTransport | None = None,
    ) -> None:
        headers = {"Accept": "application/json"}
        if api_key:
            headers["Authorization"] = f"Bearer {api_key}"
        self._http = httpx.Client(
            base_url=base_url.rstrip("/"), headers=headers, timeout=timeout, transport=transport
        )

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "UnifyUnits":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def convert(self, value: str, from_unit: str, to_unit: str) -> dict[str, Any]:
        return self._request("POST", "/v1/convert", json={"value": value, "from": from_unit, "to": to_unit})

    def convert_batch(self, conversions: Sequence[Mapping[str, str]]) -> dict[str, Any]:
        if not conversions:
            raise ValueError("At least one conversion is required")
        for conversion in conversions:
            if not all(isinstance(conversion.get(field), str) for field in ("value", "from", "to")):
                raise ValueError("Each conversion needs string value, from, and to fields")
        return self._request("POST", "/v1/batch", json={"conversions": list(conversions)})

    def categories(self) -> dict[str, Any]:
        return self._request("GET", "/v1/categories")

    def category(self, category: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/categories/{quote(category, safe='')}")

    def units(self, category: str | None = None) -> dict[str, Any]:
        params = {"category": category} if category is not None else None
        return self._request("GET", "/v1/units", params=params)

    def unit(self, unit: str) -> dict[str, Any]:
        return self._request("GET", f"/v1/units/{quote(unit, safe='')}")

    def health(self) -> dict[str, Any]:
        return self._request("GET", "/v1/health")

    def _request(self, method: str, path: str, **kwargs: Any) -> dict[str, Any]:
        response = self._http.request(method, path, **kwargs)
        try:
            response.raise_for_status()
        except httpx.HTTPStatusError as error:
            raise ApiError(error) from error
        return response.json()
