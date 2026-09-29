import httpx
import pytest
import respx

from unifyunits import ApiError, UnifyUnits


@respx.mock
def test_conversion_sends_decimal_string_and_bearer_auth():
    route = respx.post("https://api.test/v1/convert").mock(
        return_value=httpx.Response(200, json={"data": {"result": {"value": "1", "unit": "km"}}})
    )
    with UnifyUnits("test-key", base_url="https://api.test") as client:
        result = client.convert("1000", "m", "km")
    assert result["data"]["result"]["value"] == "1"
    assert route.calls[0].request.headers["Authorization"] == "Bearer test-key"
    assert route.calls[0].request.content == b'{"value":"1000","from":"m","to":"km"}'


@respx.mock
def test_batch_retains_per_item_results():
    route = respx.post("https://api.test/v1/batch").mock(
        return_value=httpx.Response(200, json={"data": [], "meta": {"total": 1, "succeeded": 1, "failed": 0}})
    )
    client = UnifyUnits("test-key", base_url="https://api.test")
    assert client.convert_batch([{"value": "1.25", "from": "m", "to": "cm"}])["meta"]["succeeded"] == 1
    assert b'"value":"1.25"' in route.calls[0].request.content
    client.close()


def test_batch_rejects_empty_input():
    client = UnifyUnits("test-key")
    with pytest.raises(ValueError):
        client.convert_batch([])
    client.close()


@respx.mock
def test_api_error_exposes_code_and_request_id():
    respx.post("https://api.test/v1/convert").mock(
        return_value=httpx.Response(400, json={"error": {"code": "UNKNOWN_UNIT", "message": "Unknown unit", "request_id": "req-1"}})
    )
    client = UnifyUnits("test-key", base_url="https://api.test")
    with pytest.raises(ApiError) as raised:
        client.convert("1", "bad", "m")
    assert raised.value.error_code == "UNKNOWN_UNIT"
    assert raised.value.request_id == "req-1"
    client.close()
