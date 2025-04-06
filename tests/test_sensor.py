"""Tests for the RAPT.io sensor platform."""

from unittest.mock import patch

from homeassistant.components.sensor import SensorDeviceClass
from homeassistant.const import UnitOfTemperature
from homeassistant.core import HomeAssistant
from homeassistant.helpers import entity_registry as er


async def test_sensors(hass: HomeAssistant, config_entry):
    """Test that sensors are created and have correct values."""
    entity_registry = er.async_get(hass)

    # Mock device and telemetry data
    mock_brewzilla_id = "a1b2c3d4-e5f6-7890-1234-567890abcdef"
    mock_brewzillas = [{"id": mock_brewzilla_id, "name": "My Test BrewZilla"}]
    mock_telemetry = {mock_brewzilla_id: {"temperature": 65.5, "status": "Mashing"}}

    with (
        patch(
            "custom_components.rapt_io.RaptApiClient.get_brewzillas",
            return_value=mock_brewzillas,
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_brewzilla",
            return_value=mock_telemetry[mock_brewzilla_id],
        ),
    ):
        await hass.config_entries.async_setup(config_entry.entry_id)
        await hass.async_block_till_done()

    # Check temperature sensor
    temp_entity_id = "sensor.my_test_brewzilla_temperature"
    temp_entity = entity_registry.async_get(temp_entity_id)
    assert temp_entity is not None
    temp_state = hass.states.get(temp_entity_id)
    assert temp_state is not None
    assert temp_state.attributes.get("device_class") == SensorDeviceClass.TEMPERATURE
    assert temp_state.attributes.get("unit_of_measurement") == UnitOfTemperature.CELSIUS

    assert float(temp_state.state) == 65.5

    # Check status sensor
    status_entity_id = "sensor.my_test_brewzilla_status"
    status_entity = entity_registry.async_get(status_entity_id)
    assert status_entity is not None

    status_state = hass.states.get(status_entity_id)
    assert status_state is not None
    assert status_state.state == "Mashing"
