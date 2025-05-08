import logging
import os

import requests

from src.client import FurthermoreClient

# Basic Example - Run this script directly to test the collector
if __name__ == "__main__":
    print("Attempting to use FurthermoreCo  lector (Example Usage)...")

    api_key_present = os.getenv(FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR)
    if not api_key_present:
        print(
            f"CRITICAL: The environment variable '{FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR}' is not set."
        )
        print(
            "Please set it before running this example (e.g., export {FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR}=your_key)."
        )
    else:
        print(
            f"Environment variable '{FurthermoreClient.FURTHERMORE_API_KEY_ENV_VAR}' is set."
        )
        example_logger = logging.getLogger("FurthermoreClientExample")
        example_logger.setLevel(logging.INFO)
        if not example_logger.hasHandlers():
            ch = logging.StreamHandler()
            formatter = logging.Formatter(
                "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
            )
            ch.setFormatter(formatter)
            example_logger.addHandler(ch)
            example_logger.propagate = False
        client = FurthermoreClient(logger=example_logger)

        try:
            print("\nFetching articles (first 3 vaults):")
            articles = client.get_articles(limit=3)
            print(
                f"Total articles (vaults) reported by API: {articles.get('count', 'N/A')}"
            )
            if articles.get("vaults"):
                for i, article in enumerate(articles["vaults"]):
                    print(
                        f"  Article {i + 1} ID: {article.get('id')}, Protocol: {article.get('metadata', {}).get('protocolName', 'N/A')}"
                    )
            else:
                print("No articles found or 'vaults' key missing in response.")

            print("\nFetching BGT prices:")
            bgt_prices = client.get_bgt_prices()
            if bgt_prices.get("data"):
                print(f"Average BGT price: {bgt_prices.get('average', 'N/A')}")
                for price_info in bgt_prices["data"][:3]:
                    print(
                        f"  Token: {price_info.get('token', 'N/A')}, Price: {price_info.get('price', 'N/A')}"
                    )
            else:
                print("No BGT prices found or 'data' key missing in response.")

            print("\nFetching sources:")
            sources = client.get_sources(vault_limit_for_scan=20)
            print(
                f"Found {len(sources['protocols'])} unique protocols: {sources['protocols'] or 'None'}"
            )
            print(
                f"Found {len(sources['incentivizers'])} unique incentivizers: {sources['incentivizers'] or 'None'}"
            )

        except ValueError as ve:
            print(f"Initialization error: {ve}")
        except requests.exceptions.RequestException as re:
            print(f"API request error: {re}")
        except Exception as e:
            print(f"An unexpected error occurred: {e}")
