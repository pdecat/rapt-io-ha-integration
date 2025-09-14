"""Platform for RAPT.io sensor integration."""

import logging

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import RaptDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up RAPT.io sensors from a config entry."""
    _LOGGER.info("Setting up RAPT.io sensor platform for entry %s", entry.entry_id)

    coordinator: RaptDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]

    entities_to_add = []

    # Enumerate devices from coordinator's device list
    for device in coordinator.devices:
        device_id = device.get("id")
        if device_id:
            device_type = device.get("deviceType")
            if device_type == "BrewZilla":
                entities_to_add.append(RaptTemperatureSensor(coordinator, device))
                entities_to_add.append(RaptStatusSensor(coordinator, device))
            elif device_type == "Hydrometer":
                entities_to_add.append(RaptTemperatureSensor(coordinator, device))
                entities_to_add.append(RaptGravitySensor(coordinator, device))
            elif device_type == "BLETemperature":
                entities_to_add.append(RaptTemperatureSensor(coordinator, device))
            else:
                _LOGGER.warning("Unsupported device type: %s", device_type)

    if entities_to_add:
        async_add_entities(entities_to_add)
    else:
        _LOGGER.warning("No entities added for config entry %s", entry.entry_id)


class RaptBaseSensor(CoordinatorEntity, SensorEntity):
    """Base class for RAPT sensors."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: RaptDataUpdateCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._device_id = device["id"]
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, self._device_id)},
            name=device.get("name"),
            manufacturer="RAPT",
            model=device.get("deviceType"),
            sw_version=device.get("firmwareVersion"),
            hw_version=device.get("id"),
        )

    @property
    def available(self) -> bool:
        """Return True if entity is available."""
        # Override CoordinatorEntity's default to check if *this* device has data
        return self._device_id in self.coordinator.data


class RaptTemperatureSensor(RaptBaseSensor):
    """Representation of a RAPT Temperature Sensor."""

    _attr_name = "Temperature"
    _attr_device_class = SensorDeviceClass.TEMPERATURE
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTemperature.CELSIUS  # Or user-configurable?
    _attr_suggested_display_precision = 1
    # _attr_entity_registry_enabled_default = False # Optional: Disable by default

    def __init__(self, coordinator: RaptDataUpdateCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self._device_id}_temperature"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        # Access temperature from coordinator data
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id].get("temperature")
        return None


class RaptStatusSensor(RaptBaseSensor):
    """Representation of a RAPT Status Sensor."""

    _attr_name = "Status"
    # Could use SensorDeviceClass.ENUM if status is a fixed set of values
    # Otherwise, leave as None
    # _attr_device_class = SensorDeviceClass.ENUM
    _attr_icon = "mdi:information"  # Or choose a more appropriate icon
    # Define options if using ENUM
    # _attr_options = ["Mashing", "Boiling", "Fermenting", "Idle", "Error"]

    def __init__(self, coordinator: RaptDataUpdateCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self._device_id}_status"

    @property
    def native_value(self) -> str | None:
        """Return the state of the sensor."""
        # Access status from coordinator data
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id].get("status")
        return None


class RaptGravitySensor(RaptBaseSensor):
    """Representation of a RAPT Gravity Sensor."""

    _attr_name = "Gravity"
    _attr_icon = "mdi:gauge"
    _attr_native_unit_of_measurement = "SG"
    _attr_suggested_display_precision = 3

    def __init__(self, coordinator: RaptDataUpdateCoordinator, device: dict) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator, device)

    @property
    def unique_id(self) -> str:
        """Return a unique ID to use for this entity."""
        return f"{DOMAIN}_{self._device_id}_gravity"

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and self._device_id in self.coordinator.data:
            return self.coordinator.data[self._device_id].get("gravity")
        return None
