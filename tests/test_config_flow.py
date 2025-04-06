"""Tests for the RAPT.io config flow."""

from unittest.mock import patch

from homeassistant import config_entries
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.const import CONF_USERNAME

from custom_components.rapt_io.const import CONF_API_KEY, DOMAIN
from custom_components.rapt_io.api import RaptAuthError, RaptApiError


async def test_form(hass):
    """Test that the form is displayed with initial fields."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})
    assert result["type"] == FlowResultType.FORM
    assert result["errors"] == {}

    # Mock validate_input to simulate successful validation
    with (
        patch(
            "custom_components.rapt_io.config_flow.validate_input",
            return_value={"title": "RAPT.io (test_username)", "unique_id": "test_device_id"},
        ),
        patch("custom_components.rapt_io.async_setup_entry", return_value=True) as mock_setup_entry,
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test_username",
                CONF_API_KEY: "test_api_key",
            },
        )
        await hass.async_block_till_done()

    assert result2["type"] == FlowResultType.CREATE_ENTRY
    assert result2["title"] == "RAPT.io (test_username)"
    assert result2["data"] == {
        CONF_USERNAME: "test_username",
        CONF_API_KEY: "test_api_key",
    }
    assert len(mock_setup_entry.mock_calls) == 1


async def test_form_invalid_auth(hass):
    """Test that we handle invalid auth."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.rapt_io.config_flow.validate_input",
        side_effect=RaptAuthError("Invalid credentials"),  # Use specific exception
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test_username",
                CONF_API_KEY: "test_api_key",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "invalid_auth"}


async def test_form_cannot_connect(hass):
    """Test that we handle cannot connect error."""
    result = await hass.config_entries.flow.async_init(DOMAIN, context={"source": config_entries.SOURCE_USER})

    with patch(
        "custom_components.rapt_io.config_flow.validate_input",
        side_effect=RaptApiError("Cannot connect"),  # Use specific exception
    ):
        result2 = await hass.config_entries.flow.async_configure(
            result["flow_id"],
            {
                CONF_USERNAME: "test_username",
                CONF_API_KEY: "test_api_key",
            },
        )

    assert result2["type"] == FlowResultType.FORM
    assert result2["errors"] == {"base": "cannot_connect"}
