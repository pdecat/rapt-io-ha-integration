"""Tests for the RAPT.io API client."""

import pytest
from unittest.mock import patch, AsyncMock

from custom_components.rapt_io.api import RaptApiClient, RaptApiError, RaptAuthError


async def test_api_client_authentication(hass):
    """Test successful authentication."""
    with patch(
        "custom_components.rapt_io.api.RaptApiClient._request",
        new_callable=AsyncMock,
        return_value={"access_token": "test_token"},
    ) as mock_request:
        client = RaptApiClient(
            username="test_username",
            api_key="test_api_key",
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )
        result = await client.authenticate()
        assert result is True
        assert client._auth_token == "test_token"
        mock_request.assert_called_once()


async def test_api_client_authentication_failure(hass):
    """Test authentication failure."""
    with patch(
        "custom_components.rapt_io.api.RaptApiClient._request",
        new_callable=AsyncMock,
        side_effect=RaptAuthError,
    ) as mock_request:
        client = RaptApiClient(
            username="test_username",
            api_key="test_api_key",
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )
        with pytest.raises(RaptAuthError):
            await client.authenticate()
        mock_request.assert_called_once()


async def test_api_client_get_brewzillas(hass):
    """Test successful BrewZilla retrieval."""
    with patch(
        "custom_components.rapt_io.api.RaptApiClient._request",
        new_callable=AsyncMock,
        return_value=[{"id": "brewzilla_1", "name": "My BrewZilla"}],
    ) as mock_request:
        client = RaptApiClient(
            username="test_username",
            api_key="test_api_key",
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )
        client._auth_token = "test_token"  # Simulate authentication
        brewzillas = await client.get_brewzillas()
        assert len(brewzillas) == 1
        assert brewzillas[0]["id"] == "brewzilla_1"
        mock_request.assert_called_once()


async def test_api_client_get_brewzilla(hass):
    """Test successful BrewZilla data retrieval."""
    with patch(
        "custom_components.rapt_io.api.RaptApiClient._request",
        new_callable=AsyncMock,
        return_value={"temperature": 25.0, "status": "Mashing"},
    ) as mock_request:
        client = RaptApiClient(
            username="test_username",
            api_key="test_api_key",
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )
        client._auth_token = "test_token"  # Simulate authentication
        data = await client.get_brewzilla(brewzilla_id="brewzilla_1")
        assert data["temperature"] == 25.0
        mock_request.assert_called_once()


async def test_api_client_request_error(hass):
    """Test API request error handling."""
    with patch(
        "custom_components.rapt_io.api.RaptApiClient._request",
        new_callable=AsyncMock,
        side_effect=RaptApiError,
    ):
        client = RaptApiClient(
            username="test_username",
            api_key="test_api_key",
            session=hass.helpers.aiohttp_client.async_get_clientsession(),
        )
        client._auth_token = "test_token"  # Simulate authentication
        with pytest.raises(RaptApiError):
            await client.get_brewzillas()
