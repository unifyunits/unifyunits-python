# UnifyUnits Python SDK

Python client for the hosted UnifyUnits Measurement API. Conversion values are
sent as decimal strings to preserve precision; the package does not bundle
conversion factors or private measurement data.

## Requirements and install

Python 3.9 or newer is required. Install the first release directly from its
GitHub tag:

```sh
python -m pip install "unifyunits @ git+https://github.com/unifyunits/unifyunits-python.git@v0.1.0"
```

After publication to PyPI, `python -m pip install unifyunits` can be used.

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

The test suite uses mocked HTTP responses and does not require a live API key.
GitHub releases and PyPI publication are separate; this repository does not
publish automatically to PyPI.
