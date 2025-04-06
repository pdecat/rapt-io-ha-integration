"""Config flow for RAPT.io integration."""

import logging

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, OptionsFlow
from homeassistant.const import CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

# Import your API client and exceptions here later
from .api import RaptApiClient, RaptApiError, RaptAuthError
from .const import (
    CONF_API_KEY,
    CONF_UPDATE_INTERVAL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    MIN_UPDATE_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_API_KEY): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, str]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA.
    """
    api_client = RaptApiClient(
        username=data[CONF_USERNAME],
        api_key=data[CONF_API_KEY],
        session=async_get_clientsession(hass),
    )

    await api_client.authenticate()
    # After successful auth, fetch devices to check connectivity and get a unique ID
    devices = await api_client.get_brewzillas()
    if not devices:
        # No devices associated with account
        raise ValueError("no_devices")

    # Use the first device's ID as the unique ID for the config entry
    # This assumes the user only cares about one Brewzilla, or that one account = one Brewzilla
    # A more complex integration might allow selecting a device.
    unique_id = devices[0]["id"]
    return {"title": f"RAPT.io ({data[CONF_USERNAME]})", "unique_id": unique_id}


class RaptConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for RAPT.io."""

    VERSION = 1

    @staticmethod
    def async_get_options_flow(config_entry):
        """Get the options flow for this handler."""
        return RaptOptionsFlowHandler(config_entry)

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
                await self.async_set_unique_id(info["unique_id"])
                self._abort_if_unique_id_configured()

                return self.async_create_entry(title=info["title"], data=user_input)
            except RaptAuthError as err:
                _LOGGER.warning("Authentication failed: %s", err)
                errors["base"] = "invalid_auth"
            except RaptApiError as err:
                _LOGGER.error("API connection error: %s", err)
                errors["base"] = "cannot_connect"
            except ValueError as err:
                if str(err) == "no_devices":
                    errors["base"] = "no_devices"
                else:
                    _LOGGER.exception("Unknown validation error: %s", err)
                    errors["base"] = "unknown"
            except Exception as err:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception in config flow: %s", err)
                errors["base"] = "unknown"

        return self.async_show_form(step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors)


class RaptOptionsFlowHandler(OptionsFlow):
    """Handle RAPT.io options."""

    def __init__(self, config_entry):
        """Initialize RAPT.io options flow."""
        self.config_entry = config_entry

    async def async_step_init(self, user_input=None):
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL),
                    ): vol.All(vol.Coerce(int), vol.Range(min=MIN_UPDATE_INTERVAL)),
                }
            ),
        )
