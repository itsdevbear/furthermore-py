# furthermore-py

A Python client for fetching data from the Furthermore API.

This client provides methods to interact with the Furthermore API endpoints for retrieving vault data (referred to as 'articles'), BGT prices, and extracting data source names (protocols and incentivizers).

## Features

- Fetch a list of articles (vaults) with pagination and sorting options.
- Fetch current BGT (Berachain Governance Token) derivative prices.
- Extract unique protocol and incentivizer names from vault data.
- Configurable base URL and logger.

## Requirements

- Python >=3.13 (as per `pyproject.toml`)
- `requests` library
- A Furthermore API key

## Installation

1.  **Clone the repository (if you haven't already):**
    ```bash
    git clone https://github.com/itsdevbear/furthermore-py
    cd furthermore-py
    ```

2.  **Install dependencies:**
    Currently, `pyproject.toml` does not list `requests`. You might need to add it or install it manually:
    ```bash
    pip install requests
    # If you update pyproject.toml to include dependencies:
    # pip install .
    ```

3.  **Set the API Key:**
    The client requires the `FURTHERMORE_API_KEY` environment variable to be set.
    ```bash
    export FURTHERMORE_API_KEY="your_actual_api_key_here"
    ```
    Alternatively, you can pass the `api_key` directly when initializing the `FurthermoreClient`.

## Usage

Here's a basic example of how to use the `FurthermoreClient`:

```python
import os
import logging
from src.client import FurthermoreClient # Adjust import based on your project structure

if __name__ == '__main__':
    # Ensure API key is set
    api_key = os.getenv(FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR)
    if not api_key:
        print(f"CRITICAL: The environment variable '{FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR}' is not set.")
        print(f"Please set it before running this example (e.g., export {FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR}=your_key).")
        exit()

    # Optional: Configure logging for the example
    example_logger = logging.getLogger("FurthermoreClientExample")
    example_logger.setLevel(logging.INFO)
    if not example_logger.hasHandlers():
        ch = logging.StreamHandler()
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
        ch.setFormatter(formatter)
        example_logger.addHandler(ch)
        example_logger.propagate = False # Avoid duplicate logs if root logger is configured

    client = FurthermoreClient(logger=example_logger)

    try:
        print("\nFetching articles (first 3 vaults):")
        articles = client.get_articles(limit=3)
        print(f"Total articles (vaults) reported by API: {articles.get('count', 'N/A')}")
        if articles.get("vaults"):
            for i, article in enumerate(articles["vaults"]):
                print(f"  Article {i+1} ID: {article.get('id')}, Protocol: {article.get('metadata', {}).get('protocolName', 'N/A')}")
        else:
            print("No articles found or 'vaults' key missing in response.")

        print("\nFetching BGT prices:")
        bgt_prices = client.get_bgt_prices()
        if bgt_prices.get("data"):
            print(f"Average BGT price: {bgt_prices.get('average', 'N/A')}")
            for price_info in bgt_prices["data"][:3]: 
                print(f"  Token: {price_info.get('token', 'N/A')}, Price: {price_info.get('price', 'N/A')}")
        else:
            print("No BGT prices found or 'data' key missing in response.")

        print("\nFetching sources:")
        sources = client.get_sources(vault_limit_for_scan=20) 
        print(f"Found {len(sources['protocols'])} unique protocols: {sources['protocols'] or 'None'}")
        print(f"Found {len(sources['incentivizers'])} unique incentivizers: {sources['incentivizers'] or 'None'}")

    except ValueError as ve:
        print(f"Initialization error: {ve}")
    except requests.exceptions.RequestException as re:
        print(f"API request error: {re}")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")
```

To run the example script (e.g., if it's `src/examples/basic.py`):

```bash
python src/examples/basic.py
```

## API Documentation

For more details on the API endpoints and responses, refer to the unofficial Gist:
[https://gist.github.com/asianviking/b87cad7b9e0b0519f1ae8bdb8121398b](https://gist.github.com/asianviking/b87cad7b9e0b0519f1ae8bdb8121398b)

## Contributing

(Details on how to contribute to this project, if applicable.)

## License

(Specify the license for this project, e.g., MIT, Apache 2.0.)
