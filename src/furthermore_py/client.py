import logging
import os
from typing import Any

import requests

module_logger = logging.getLogger(__name__)
if not logging.getLogger().hasHandlers():
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    )


class FurthermoreClient:
    """
    A client for fetching data from the Furthermore API.

    This class provides methods to interact with the Furthermore API endpoints
    for retrieving vault data (referred to as 'articles'), BGT prices, and
    extracting data source names (protocols and incentivizers).

    API Key: Requires the `FURTHERMORE_API_KEY` environment variable to be set, or
    an API key to be passed during initialization.

    API Documentation (Unofficial Gist):
    https://gist.github.com/asianviking/b87cad7b9e0b0519f1ae8bdb8121398b
    """

    DEFAULT_BASE_URL = "https://pre.furthermore.app/api/v1"
    FURTHERMORE_API_KEY_ENV_VAR = "FURTHERMORE_API_KEY"

    def __init__(
        self,
        base_url: str | None = None,
        api_key: str | None = None,
        logger: logging.Logger | None = None,
    ):
        """
        Initializes the FurthermoreClient.

        Args:
            base_url: The base URL for the Furthermore API.
                      Defaults to `DEFAULT_BASE_URL`.
            api_key: The API key for authentication.
                     Defaults to the value of the `FURTHERMORE_API_KEY_ENV_VAR` environment variable.
            logger: A specific logger instance to use.
                    Defaults to the module-level logger (`furthermore.py`'s logger).

        Raises:
            ValueError: If the API key is not provided and not found in environment variables.
        """
        self.base_url = base_url or self.DEFAULT_BASE_URL
        self.api_key = api_key or os.getenv(self.FURTHERMORE_API_KEY_ENV_VAR)
        self.logger = logger or module_logger

        if not self.api_key:
            msg = f"API key not provided and not found in environment variable '{self.FURTHERMORE_API_KEY_ENV_VAR}'."
            self.logger.error(msg)
            raise ValueError(msg)

        self.headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }
        self.logger.info(
            f"FurthermoreClient initialized with base URL: {self.base_url}"
        )

    def _make_request(
        self,
        method: str,
        endpoint: str,
        params: dict[str, Any] | None = None,
        data: dict[str, Any] | None = None,
    ) -> dict[str, Any]:
        """
        Helper function to make HTTP requests to the Furthermore API.

        Args:
            method: HTTP method (e.g., "GET", "POST").
            endpoint: API endpoint path (e.g., "/vaults"). This should start with a '/'.
            params: URL query parameters for the request.
            data: JSON body for the request (for POST, PUT, etc.).

        Returns:
            The JSON response from the API parsed as a dictionary.

        Raises:
            requests.exceptions.HTTPError: For HTTP error responses (4xx or 5xx).
            requests.exceptions.Timeout: If the request times out.
            requests.exceptions.ConnectionError: For network-related errors.
            requests.exceptions.RequestException: For other request-related issues or if the API returns an error message in its JSON body.
        """
        url = f"{self.base_url.rstrip('/')}{endpoint}"
        self.logger.debug(
            f"Making {method} request to {url} with params: {params}, data: {data}"
        )
        try:
            response = requests.request(
                method, url, headers=self.headers, params=params, json=data, timeout=10
            )  # Added timeout
            response.raise_for_status()  # Raises HTTPError for bad responses
            return response.json()
        except requests.exceptions.HTTPError as http_err:
            self.logger.error(
                f"HTTP error occurred while requesting {url}: {http_err} - Response: {http_err.response.text}"
            )
            try:
                error_content = http_err.response.json()
                if "error" in error_content:
                    # Re-raise with a more specific message from the API if available
                    raise requests.exceptions.RequestException(
                        f"API Error for {url}: {error_content['error']} (Status {http_err.response.status_code})"
                    ) from http_err
            except ValueError:  # If error response is not JSON
                pass  # Original HTTPError will be raised
            raise
        except requests.exceptions.RequestException as req_err:
            self.logger.error(
                f"Request exception occurred while requesting {url}: {req_err}"
            )
            raise

    def _extract_and_add_name(
        self, data: dict | None, path: tuple[str, ...], target_set: set[str]
    ):
        """
        Safely extracts a name from a nested dictionary path and adds it to the target set
        if the name is a non-empty string.

        Args:
            data: The dictionary to extract from (e.g., metadata).
            path: A tuple of keys representing the path to the name.
            target_set: The set to add the validated name to.
        """
        if not isinstance(data, dict):
            return

        current_level = data
        for key in path[:-1]:
            current_level = current_level.get(key)
            if not isinstance(current_level, dict):
                return

        name_value = current_level.get(path[-1])
        if isinstance(name_value, str):
            stripped_name = name_value.strip()
            if stripped_name:
                target_set.add(stripped_name)

    def get_vaults(
        self,
        offset: int = 0,
        limit: int = 10,
        sort_by: str | None = None,
        sort_direction: str | None = None,
    ) -> dict[str, Any]:
        """
        Fetches a list of vaults from the API's `/vaults` endpoint.

        Args:
            offset: Number of records to skip (for pagination).
            limit: Maximum number of records to return per page.
            sort_by: Field to sort the results by (e.g., 'tvl', 'apr', 'allTimeReceivedBGTAmount').
            sort_direction: Direction for sorting ('asc' or 'desc').

        Returns:
            A dictionary representing the JSON response from the API.
            Expected structure includes a "vaults" key (list of vault objects)
            and a "count" key (total number of vaults).
            Example vault object fields: 'id', 'beraVault', 'integratedVaults', 'pool', 'metadata'.
        """
        params: dict[str, Any] = {"offset": offset, "limit": limit}
        if sort_by:
            params["sortBy"] = sort_by
        if sort_direction:
            params["sortDirection"] = sort_direction

        self.logger.info(
            f"Fetching articles (vaults) from /vaults with params: {params}"
        )
        return self._make_request("GET", "/vaults", params=params)

    def get_bgt_prices(self) -> dict[str, Any]:
        """
        Fetches the current prices for BGT (Berachain Governance Token) derivatives
        from the API's `/bgt/prices` endpoint.

        Returns:
            A dictionary representing the JSON response from the API.
            Expected structure includes a "data" key (list of token price objects)
            an "average" key (average price), and a "count" key (number of tokens).
            Example token price object: {'token': 'iBGT', 'price': 5.27...}.
        """
        self.logger.info("Fetching BGT prices from /bgt/prices.")
        return self._make_request("GET", "/bgt/prices")

    def get_sources(self, vault_limit_for_scan: int = 100) -> dict[str, set[str]]:
        """
        Extracts unique source names (protocols and incentivizers) by analyzing vault data.
        This method calls `get_vaults` to fetch a sample of vaults and extracts
        protocol and incentivizer names from their metadata.

        Args:
            vault_limit_for_scan: The number of vaults to fetch and scan for source names.
                                    A higher number provides a more comprehensive list but takes longer.

        Returns:
            A dictionary with two keys:
            - "protocols": A set of unique protocol names found (e.g., "Kodiak", "Infrared").
            - "incentivizers": A set of unique incentivizer names found.
            Returns empty sets if an API error occurs during vault fetching.
        """
        self.logger.info(
            f"Fetching sources by analyzing up to {vault_limit_for_scan} vaults."
        )
        protocols: set[str] = set()
        incentivizers: set[str] = set()
        try:
            vault_data = self.get_vaults(limit=vault_limit_for_scan)

            for vault in vault_data.get("vaults", []):
                metadata = vault.get("metadata")
                self._extract_and_add_name(metadata, ("protocolName",), protocols)
                self._extract_and_add_name(metadata, ("protocol", "name"), protocols)
                self._extract_and_add_name(
                    metadata, ("incentivizer", "name"), incentivizers
                )

            self.logger.info(
                f"Found {len(protocols)} unique protocols and {len(incentivizers)} unique incentivizers."
            )
            return {"protocols": protocols, "incentivizers": incentivizers}
        except requests.exceptions.RequestException as e:
            self.logger.error(
                f"Could not fetch sources due to an API error during vault retrieval: {e}"
            )
            return {"protocols": set(), "incentivizers": set()}
