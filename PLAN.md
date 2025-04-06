# Home Assistant RAPT.io Integration Plan

This document outlines the plan for creating a Home Assistant custom integration for RAPT.io devices, specifically targeting the Brewzilla 4.

**Goal:** Integrate RAPT.io Brewzilla 4 into Home Assistant to monitor temperature and brewing status using the official RAPT.io Cloud API.

**API Documentation:** [https://gitlab.com/rapt.io/public/-/wikis/RAPT%20API](https://gitlab.com/rapt.io/public/-/wikis/RAPT%20API)

## Phases

**Phase 1: Research & Foundation**

1.  **RAPT.io API Investigation:**
    *   **Goal:** Understand how to communicate with the RAPT.io cloud API using the provided documentation.
    *   **Tasks:**
        *   Determine the authentication method (likely Token-based based on docs).
        *   Identify the specific API endpoints required:
            *   `/api/token/` (for authentication)
            *   `/api/v1/devices/` (for device list)
            *   `/api/v1/telemetry/` (for temperature/status data)
        *   Analyze the structure of the data returned by the API (JSON).
        *   Note any rate limits or usage constraints.

2.  **Project Structure Setup:**
    *   **Goal:** Create the basic file and directory layout for the custom integration.
    *   **Tasks:**
        *   Create the main directory: `custom_components/rapt_io/`
        *   Create initial placeholder files:
            *   `__init__.py`
            *   `manifest.json`
            *   `const.py`
            *   `config_flow.py`
            *   `api.py`
            *   `sensor.py`
            *   `coordinator.py`

**Phase 2: Core Implementation**

3.  **API Client Implementation (`api.py`):**
    *   **Goal:** Build the Python code to interact with the RAPT.io API.
    *   **Tasks:**
        *   Implement functions using `aiohttp` for:
            *   Authenticating with the API.
            *   Fetching the list of devices.
            *   Fetching the latest telemetry data for a specific device.
        *   Include robust error handling.
        *   Parse the JSON responses.

4.  **Configuration Flow (`config_flow.py`):**
    *   **Goal:** Allow users to add and configure the integration via the Home Assistant UI.
    *   **Tasks:**
        *   Implement a `ConfigFlow` handler.
        *   Define UI steps to collect username and password.
        *   Validate the credentials by making a test API call.
        *   Store the validated credentials securely.
        *   Potentially allow device selection.

5.  **Data Update Coordinator (`coordinator.py`):**
    *   **Goal:** Efficiently manage polling the RAPT.io API for updates.
    *   **Tasks:**
        *   Implement a class inheriting from `DataUpdateCoordinator`.
        *   Use the `api.py` client to periodically fetch the latest data.
        *   Manage update intervals and handle API errors centrally.

**Phase 3: Entity Creation & Finalization**

6.  **Sensor Implementation (`sensor.py`):**
    *   **Goal:** Create the Home Assistant sensor entities.
    *   **Tasks:**
        *   Define sensor entity classes (e.g., `RaptTemperatureSensor`, `RaptStatusSensor`).
        *   Link the sensors to the `DataUpdateCoordinator`.
        *   Map the fetched data to sensor state and attributes.
        *   Define units, device classes, and icons.

7.  **Integration Setup (`__init__.py`):**
    *   **Goal:** Tie all the components together.
    *   **Tasks:**
        *   Implement `async_setup_entry` to instantiate API client, coordinator, and set up platforms.
        *   Implement `async_unload_entry` for cleanup.

8.  **Metadata & Dependencies (`manifest.json`):**
    *   **Goal:** Define the integration's properties and requirements.
    *   **Tasks:**
        *   Finalize fields: `domain`, `name`, `version`, `documentation`, `codeowners`, `iot_class`.
        *   List `requirements` (e.g., `aiohttp`).

9.  **Documentation (`README.md`):**
    *   **Goal:** Provide users with instructions.
    *   **Tasks:**
        *   Write installation, configuration, and usage instructions.

## Visual Overview

```mermaid
graph LR
    subgraph User Interface
        UI(HA Frontend) -- Config Data --> CF(config_flow.py);
    end

    subgraph Core Logic
        CF -- Credentials --> Init(init.py);
        Init -- Sets up --> Coord(coordinator.py);
        Init -- Sets up --> Sensor(sensor.py);
        Coord -- Uses --> API(api.py);
        Sensor -- Gets Data From --> Coord;
    end

    subgraph External
        API -- HTTP Requests --> RAPT[RAPT.io Cloud API];
    end

    subgraph Metadata
        Manifest(manifest.json);
    end

    Init -- Reads --> Manifest;
    style RAPT fill:#f9f,stroke:#333,stroke-width:2px
