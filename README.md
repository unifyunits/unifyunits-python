# UnifyUnits Python SDK

Python client for the hosted UnifyUnits Measurement API. Conversion values are
sent as decimal strings to preserve precision; the package does not bundle
conversion factors or private measurement data.

## Install

```sh
pip install unifyunits
```

## Usage

```python
from unifyunits import UnifyUnits

with UnifyUnits(api_key="uu_live_your_key") as client:
    result = client.convert("1000", "m", "km")
    print(result["data"]["result"])  # {"value": "1", "unit": "km"}
```

Set `base_url` for a compatible deployment. API keys should stay in server-side
secret configuration and must not be committed or exposed to browser clients.

Available methods are `convert`, `convert_batch`, `categories`, `category`,
`units`, `unit`, and `health`. `ApiError` exposes `error_code`, `request_id`,
and `details` for structured API failures. Network and timeout errors remain
`httpx` exceptions.

## Development

```sh
python -m venv .venv
. .venv/bin/activate
pip install -e '.[test]'
pytest
```

Release and PyPI publication are separate steps.
