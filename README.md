# Home Assistant Integration for IKEA OBEGRÄNSAD

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)

Home Assistant integration for the IKEA OBEGRÄNSAD LED matrix clock running the [IkeaObegraensad firmware](https://github.com/Abrechen2/IkeaObegraensad).

Communicates with the device over plain HTTP (local polling) and auto-discovers it via mDNS — no MQTT required.

## Features

- **Display on/off** — control the matrix from Home Assistant
- **Effect picker** — switch between all matrix effects (Snake, Clock, Rain, …)
- **Brightness** — 0–255 slider, also exposed as a Light entity
- **Auto-brightness** — automatic adjustment from the on-board LDR
- **Timezone** — set the clock's timezone
- **Sensors** — current time, current effect, brightness, IP address, ambient light
- **Presence status** — exposes the device's presence flag (if used externally)
- **Device page** — full device page with metadata and diagnostics
- **Diagnostics** — detailed diagnostic info inside Home Assistant
- **Automations** — every entity is usable in HA automations
- **mDNS discovery** — devices on the local network are detected automatically
- **Independent of MQTT** — works in parallel to any MQTT control channel on the device

## Installation

### Via HACS (recommended)

1. Open HACS
2. Integrations → three-dot menu → **Custom repositories**
3. Repository URL: `https://github.com/Abrechen2/ikea-obegraensad-homeassistant`
4. Category: **Integration**
5. Click **Add**
6. Install the integration
7. Restart Home Assistant

### Manual installation

1. Copy the `custom_components/ikea_obegraensad/` folder into your `config/custom_components/` directory
2. Restart Home Assistant
3. Go to **Settings → Devices & Services → Add Integration → IKEA Obegraensad**

## Configuration

1. Open Home Assistant
2. Go to **Settings → Devices & Services**
3. Click **+ Add Integration**
4. Search for **IKEA Obegraensad**
5. Enter the device's IP address (e.g. `192.168.1.100`)
6. Optional: change the port (default `80`)
7. Optional: give it a name

## Usage

After installation the following entities are created and grouped under one device:

### Entities

| Type | Entity | Description |
|------|--------|-------------|
| Switch | Display | Display on/off |
| Switch | Auto Brightness | Toggle automatic brightness adjustment |
| Select | Effect | Pick the active effect (Snake, Clock, Rain, …) |
| Select | Timezone | Pick the device timezone |
| Light  | Brightness | Brightness control (also usable as a Light entity) |
| Sensor | Time | Current time on the device |
| Sensor | Current Effect | Currently running effect |
| Sensor | Brightness | Current brightness |
| Sensor | Sensor Value | Ambient light sensor reading |
| Sensor | IP Address | Device IP |
| Binary Sensor | Presence | Presence status (if used externally) |
| Binary Sensor | Display Status | Display power state |

### Device page

Each configured device gets a full device page in Home Assistant with:

- **Device info:** name, manufacturer (IKEA), model (Obegraensad), firmware version, link to the web interface
- **Diagnostics card:** full status JSON from `/api/status`, config-entry info, coordinator status
- **All entities** grouped under the device
- **Activity log** auto-generated from entity state changes

The device page is accessible under **Settings → Devices & Services → [Device]**.

### Service: Configure auto-brightness

The service `ikea_obegraensad.configure_auto_brightness` exposes the advanced auto-brightness configuration:

```yaml
service: ikea_obegraensad.configure_auto_brightness
data:
  entity_id: switch.ikea_clock_auto_brightness
  enabled: true
  min: 50         # minimum brightness (0-1023)
  max: 800        # maximum brightness (0-1023)
  sensor_min: 100 # minimum sensor value (0-1024)
  sensor_max: 900 # maximum sensor value (0-1024)
```

### Automation examples

```yaml
automation:
  # Living room light on -> display on
  - alias: "Living room light -> display on"
    trigger:
      - platform: state
        entity_id: light.living_room
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_display

  # Enable auto-brightness at sunset
  - alias: "Auto-brightness at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_auto_brightness

  # Switch to clock effect every evening at 8 PM
  - alias: "Evening clock effect"
    trigger:
      - platform: time
        at: "20:00:00"
    action:
      - service: select.select_option
        target:
          entity_id: select.ikea_clock_effect
        data:
          option: "clock"
```

## Firmware requirements

The Arduino device must expose the following API endpoints:

- `GET /api/status` — returns JSON status data
  Expected fields: `displayEnabled`, `brightness`, `currentEffect`, `time`, `presence`, `sensorValue`, `ipAddress`, `autoBrightnessEnabled`, `autoBrightnessMin`, `autoBrightnessMax`, `autoBrightnessSensorMin`, `autoBrightnessSensorMax`, `timezone`
- `GET /api/setDisplay?enabled=true|false` — display on/off
- `GET /api/setBrightness?b=0-1023` — set brightness
- `GET /effect/{effect_name}` — switch effect
- `GET /api/setAutoBrightness?enabled=true|false&min=0-1023&max=0-1023&sensorMin=0-1024&sensorMax=0-1024` — configure auto-brightness
- `GET /api/setTimezone?tz=Europe/Berlin` — set timezone

The matching firmware lives in [Abrechen2/IkeaObegraensad](https://github.com/Abrechen2/IkeaObegraensad).

## Requirements

- Home Assistant 2023.1.0 or newer
- IKEA OBEGRÄNSAD device running firmware that supports `/api/setDisplay`

## Known limitations

- The integration uses polling (every 30 seconds) for status updates
- Display control works in parallel to any external MQTT control
- The timezone select only contains the most common timezones (~25)

## Support

Please open a GitHub issue if you run into problems.
