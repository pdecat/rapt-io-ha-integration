"""DataUpdateCoordinator for the RAPT.io integration."""

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

# Import API client and exceptions
from .api import RaptApiClient, RaptApiError, RaptAuthError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

# Define update interval (adjust as needed, consider API rate limits)


class RaptDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching RAPT.io data."""

    def __init__(self, hass: HomeAssistant, client: RaptApiClient, update_interval: int) -> None:
        """Initialize global RAPT data updater."""
        self.client = client
        self.devices = []  # Store device list

        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=timedelta(seconds=update_interval),
        )

    async def _async_update_data(self) -> dict:
        """Fetch data from API endpoint.

        This is the place to fetch data from your API service.
        """
        _LOGGER.debug("Starting data update cycle")
        try:
            # 1. Get the list of devices (if not already stored)
            if not self.devices:
                brewzillas = await self.client.get_brewzillas()
                bonded_devices = await self.client.get_bonded_devices()
                hydrometers = await self.client.get_hydrometers()
                self.devices = brewzillas + bonded_devices + hydrometers
                _LOGGER.debug("Fetched device list: %s", self.devices)

            # 2. Iterate through devices and fetch data for each
            telemetry_data = {}
            for device in self.devices:
                device_id = device.get("id")
                if device_id:
                    try:
                        # BrewZillas have a 'telemetry' object in their GetBrewZillas response
                        # Bonded devices do not. This is a heuristic to differentiate them.
                        device_type = device.get("deviceType")
                        if device_type == "BrewZilla":
                            data = await self.client.get_brewzilla(device_id)
                        elif device_type == "Hydrometer":
                            data = await self.client.get_hydrometer(device_id)
                        elif device_type == "BLETemperature":
                            data = await self.client.get_bonded_device(device_id)
                        else:
                            _LOGGER.warning("Unsupported device type: %s", device_type)
                            data = None
                        if data:
                            telemetry_data[device_id] = data
                    except RaptApiError as err:
                        # Log individual device fetch errors, but continue updating others
                        _LOGGER.warning("Failed to fetch data for device %s: %s", device_id, err)

            _LOGGER.debug("Telemetry data: %s", telemetry_data)
            return telemetry_data

        except RaptAuthError as err:
            # Authentication errors likely require re-configuration
            _LOGGER.error("Authentication error during update: %s", err)
            # Trigger re-authentication flow? Or just raise UpdateFailed?
            # For now, treat as a failure to update.
            raise UpdateFailed(f"Authentication error: {err}") from err
        except RaptApiError as err:
            _LOGGER.error("API error during update: %s", err)
            raise UpdateFailed(f"Error communicating with API: {err}") from err
        except Exception as err:
            _LOGGER.exception("Unexpected error during data update")
            raise UpdateFailed(f"Unexpected error: {err}") from err
