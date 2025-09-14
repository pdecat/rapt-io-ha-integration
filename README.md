# RAPT.io Home Assistant Integration

This custom integration allows you to integrate your RAPT.io devices, such as the Brewzilla, into Home Assistant.

## Installation

### HACS (Recommended)

1.  Ensure that you have the [HACS](https://hacs.xyz/) integration installed.
2.  Add this repository as a custom repository in HACS:
    *   URL: `https://github.com/pdecat/rapt-io-ha-integration`
    *   Category: Integration
3.  Install the "RAPT.io" integration from HACS.

### Manual Installation

1.  Copy the `custom_components/rapt_io` directory to your Home Assistant's `custom_components` directory.
2.  Restart Home Assistant.

## Configuration

1.  Go to "Configuration" -> "Integrations" in your Home Assistant UI.
2.  Click the "+" button and search for "RAPT.io".
3.  Enter your RAPT.io username and API Key.
4.  The integration will automatically discover your RAPT.io devices and create sensors for temperature and status.
### Options

You can configure the polling frequency for this integration. A lower value means sensors will update more frequently, but will also increase the number of requests made to the RAPT API. Be mindful of the API usage warnings.

1.  Go to "Configuration" -> "Integrations".
2.  Find the RAPT.io integration and click "Configure".
3.  Adjust the "Update interval" (in seconds). The default is 60 seconds.

## Usage

The integration will create the following sensors for each supported RAPT.io device:

### BrewZilla
*   `sensor.brewzilla_name_temperature`: The current temperature of the BrewZilla.
*   `sensor.brewzilla_name_status`: The current status of the BrewZilla (e.g., Mashing, Boiling).

### Bonded Devices (e.g., BLE Thermometers)
*   `sensor.bonded_device_name_temperature`: The current temperature of the bonded device.

### Hydrometers (e.g., RAPT Pill)
*   `sensor.hydrometer_name_temperature`: The current temperature of the hydrometer.
*   `sensor.hydrometer_name_gravity`: The current gravity reading of the hydrometer.

## Troubleshooting

*   If you have issues, check the Home Assistant logs for errors related to the `rapt_io` integration.
*   Ensure that your RAPT.io username and API Key are correct.
*   If you still have problems, please open an issue on the [GitHub repository](https://github.com/pdecat/rapt-io-ha-integration/issues).

## Important Notes

### API Secrets

Before you can obtain a bearer token, you will require an Api Secret. Login to the RAPT App and navigate to "My Account / Api Secrets". From here you can create an Api Secret. Please note that once a secret has been created, it is hashed and unrecoverable. You will need to record the secret when it is shown to you, as you will not be able to see it again from the RAPT App.

### Support & API [Mis]Use

*   Access to the Api is unsupported. This means you will not be able to get assistance from KegLand directly.
*   If your use of the Api causes problems with your Rapt account or devices, this is on you. We track all Api requests, so if you destroy a device through misuse of the Api, it will void your warranty.
*   If your use of the Api causes problems with other Rapt users, depending on the severity of the problem, you will be given a warning and/or your access to the Api will be revoked.
*   The Api (endpoints, parameters, response models etc.) is subject to change without notice.

## Development

This project uses `uv` for managing the virtual environment and dependencies, and `ruff` for linting and formatting.

To set up the development environment:

```bash
uv venv
uv pip install -e .[dev]
```

To run the tests:

```bash
uv run pytest custom_components/rapt_io/tests
```

To lint and format the code:

```bash
ruff check . --fix
ruff format .
```


## TODO

The following features are planned for future releases:

*   Ability to backfill historical telemetry data.
*   Support for managing and interacting with brewing profiles.
