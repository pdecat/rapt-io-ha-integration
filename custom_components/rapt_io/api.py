"""RAPT.io API Client."""

import asyncio
import logging
import socket

import aiohttp
from aiohttp import ClientError, ClientResponseError

_LOGGER = logging.getLogger(__name__)

# Define API base URL (adjust if needed based on documentation)
RAPT_API_BASE_URL = "https://api.rapt.io"
RAPT_AUTH_URL = "https://id.rapt.io"


# Define custom exceptions
class RaptApiError(Exception):
    """Generic RAPT API communication error."""


class RaptAuthError(RaptApiError):
    """Failed to authenticate with RAPT API."""


class RaptApiClient:
    """RAPT.io API Client."""

    def __init__(self, username: str, api_key: str, session: aiohttp.ClientSession | None = None) -> None:
        """Initialize the API client."""
        self._username = username
        self._api_key = api_key
        # TODO: Implement token storage and management
        self._auth_token = None
        self._session = session or aiohttp.ClientSession()
        self._base_url = RAPT_API_BASE_URL

    async def _request(self, method: str, url: str, data: dict | None = None, is_auth: bool = False) -> dict:
        """Make an API request."""
        headers = {}
        if self._auth_token:
            headers["Authorization"] = f"Bearer {self._auth_token}"  # Assuming Bearer token

        _LOGGER.debug("Sending %s request to %s", method, url)
        try:
            async with self._session.request(
                method,
                url,
                data=data if is_auth else None,
                json=data if not is_auth else None,
                headers=headers,
                timeout=15,  # Increased timeout
            ) as response:
                response.raise_for_status()  # Raise exception for 4xx/5xx status codes
                _LOGGER.debug("API Response status: %s", response.status)
                json_response = await response.json()
                _LOGGER.debug("API Response data: %s", json_response)
                return json_response
        except ClientResponseError as err:
            if err.status == 401:  # Unauthorized
                _LOGGER.error("Authentication error: %s", err)
                raise RaptAuthError("Authentication failed") from err
            _LOGGER.error("HTTP error during API request to %s: %s", url, err)
            raise RaptApiError(f"Request failed: {err}") from err
        except (ClientError, socket.gaierror, asyncio.TimeoutError) as err:
            _LOGGER.error("Network error during API request to %s: %s", url, err)
            raise RaptApiError(f"Communication error: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during API request to %s", url)
            raise RaptApiError(f"An unexpected error occurred: {err}") from err

    async def authenticate(self) -> bool:
        """Authenticate with the API and store the token."""
        _LOGGER.info("Attempting to authenticate with RAPT.io API for user %s", self._username)
        self._auth_token = None
        auth_url = f"{RAPT_AUTH_URL}/connect/token"
        auth_data = {
            "client_id": "rapt-user",
            "grant_type": "password",
            "username": self._username,
            "password": self._api_key,
        }

        try:
            # Authentication request uses form-urlencoded data
            response = await self._request("post", auth_url, data=auth_data, is_auth=True)
            self._auth_token = response.get("access_token")
            if not self._auth_token:
                _LOGGER.error("Authentication successful but no access token received: %s", response)
                raise RaptAuthError("Authentication successful but no access token received")
            _LOGGER.info("Authentication successful, token acquired.")
            return True
        except RaptAuthError as err:
            raise err
        except RaptApiError as err:
            _LOGGER.error("Authentication failed due to API/network error: %s", err)
            raise RaptAuthError(f"Authentication failed: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during authentication")
            raise RaptAuthError(f"An unexpected error occurred during authentication: {err}") from err

    async def get_brewzillas(self) -> list[dict]:
        """Fetch the list of BrewZilla devices from the API."""
        _LOGGER.info("Fetching BrewZillas from RAPT.io API")
        if not self._auth_token:
            _LOGGER.debug("No auth token found, attempting authentication first.")
            await self.authenticate()

        try:
            url = f"{self._base_url}/api/BrewZillas/GetBrewZillas"
            response = await self._request("get", url)
            if isinstance(response, list):
                _LOGGER.debug("Received %d BrewZillas", len(response))
                return response
            else:
                _LOGGER.error("Unexpected BrewZilla list format received: %s", response)
                raise RaptApiError("Unexpected format for BrewZilla list")
        except RaptApiError as err:
            _LOGGER.error("Failed to fetch BrewZillas: %s", err)
            raise err

    async def get_brewzilla(self, brewzilla_id: str) -> dict:
        """Fetch the latest data for a specific BrewZilla."""
        _LOGGER.info("Fetching data for BrewZilla %s", brewzilla_id)
        if not self._auth_token:
            _LOGGER.debug("No auth token found, attempting authentication first.")
            await self.authenticate()

        try:
            url = f"{self._base_url}/api/BrewZillas/GetBrewZilla?brewZillaId={brewzilla_id}"
            response = await self._request("get", url)
            if isinstance(response, dict):
                _LOGGER.debug("BrewZilla data received: %s", response)
                return response
            else:
                _LOGGER.error("Unexpected BrewZilla data format received: %s", response)
                raise RaptApiError("Unexpected format for BrewZilla data")
        except RaptApiError as err:
            _LOGGER.error("Failed to fetch data for BrewZilla %s: %s", brewzilla_id, err)
            raise err

    async def close(self) -> None:
        """Close the underlying session if it wasn't passed in."""
        if self._session and not isinstance(self._session, aiohttp.ClientSession):
            # If session was passed in, caller is responsible for closing
            pass
        elif self._session:
            await self._session.close()
            _LOGGER.debug("Closed internal aiohttp session")

    async def __aenter__(self):
        """Async context manager enter."""
        return self

    async def __aexit__(self, exc_type, exc, tb):
        """Async context manager exit."""
        await self.close()
