"""Fixtures for the RAPT.io integration."""

from collections.abc import Generator
from typing import Any
from unittest.mock import patch

import pytest
from pytest_homeassistant_custom_component.common import MockConfigEntry
from pytest_homeassistant_custom_component.plugins import enable_custom_integrations  # noqa: F401

from custom_components.rapt_io.const import CONF_API_KEY, DOMAIN


# This fixture is used to mock the config entry.
@pytest.fixture(name="config_entry")
def mock_config_entry(hass):
    """Create a mock config entry for testing."""
    entry = MockConfigEntry(
        domain=DOMAIN,
        title="RAPT.io",
        data={
            "username": "test_username",
            CONF_API_KEY: "test_api_key",
        },
        unique_id="test_device_id",
    )
    entry.add_to_hass(hass)
    return entry


# This fixture is used to prevent HomeAssistant from attempting to create and dismiss persistent
# notifications. These calls would fail without this fixture since the persistent_notification
# integration is never loaded during a test.
@pytest.fixture(name="skip_notifications")
def skip_notifications_fixture() -> Generator:
    """Skip notification calls."""
    with (
        patch("homeassistant.components.persistent_notification.async_create"),
        patch("homeassistant.components.persistent_notification.async_dismiss"),
    ):
        yield


@pytest.fixture(autouse=True)
def rapt_io_fixture(
    skip_notifications: Any,
    enable_custom_integrations: Any,  # noqa: F811
    hass: Any,
) -> None:
    """Automatically use an ordered combination of fixtures."""
