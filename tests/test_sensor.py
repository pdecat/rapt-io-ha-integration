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
    mock_brewzillas = [{"id": mock_brewzilla_id, "name": "My Test BrewZilla", "telemetry": {}}]
    mock_bonded_device_id = "e5f6a1b2-c3d4-5678-9012-345678abcdef"
    mock_bonded_devices = [{"id": mock_bonded_device_id, "name": "My BLE Thermometer", "type": "Thermometer"}]
    mock_hydrometer_id = "f1e2d3c4-b5a6-7890-1234-567890abcdef"
    mock_hydrometers = [{"id": mock_hydrometer_id, "name": "My RAPT Pill", "gravity": 1.050}]
    mock_data = {
        mock_brewzilla_id: {"temperature": 65.5, "status": "Mashing"},
        mock_bonded_device_id: {"temperature": 22.2},
        mock_hydrometer_id: {"temperature": 20.0, "gravity": 1.052},
    }

    with (
        patch(
            "custom_components.rapt_io.RaptApiClient.get_brewzillas",
            return_value=mock_brewzillas,
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_bonded_devices",
            return_value=mock_bonded_devices,
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_hydrometers",
            return_value=mock_hydrometers,
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_brewzilla",
            return_value=mock_data[mock_brewzilla_id],
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_bonded_device",
            return_value=mock_data[mock_bonded_device_id],
        ),
        patch(
            "custom_components.rapt_io.RaptApiClient.get_hydrometer",
            return_value=mock_data[mock_hydrometer_id],
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

    # Check bonded device temperature sensor
    bonded_temp_entity_id = "sensor.my_ble_thermometer_temperature"
    bonded_temp_entity = entity_registry.async_get(bonded_temp_entity_id)
    assert bonded_temp_entity is not None

    bonded_temp_state = hass.states.get(bonded_temp_entity_id)
    assert bonded_temp_state is not None
    assert float(bonded_temp_state.state) == 22.2

    # Check hydrometer sensors
    hydrometer_temp_entity_id = "sensor.my_rapt_pill_temperature"
    hydrometer_temp_entity = entity_registry.async_get(hydrometer_temp_entity_id)
    assert hydrometer_temp_entity is not None

    hydrometer_temp_state = hass.states.get(hydrometer_temp_entity_id)
    assert hydrometer_temp_state is not None
    assert float(hydrometer_temp_state.state) == 20.0

    hydrometer_gravity_entity_id = "sensor.my_rapt_pill_gravity"
    hydrometer_gravity_entity = entity_registry.async_get(hydrometer_gravity_entity_id)
    assert hydrometer_gravity_entity is not None

    hydrometer_gravity_state = hass.states.get(hydrometer_gravity_entity_id)
    assert hydrometer_gravity_state is not None
    assert float(hydrometer_gravity_state.state) == 1.052
