# Home Assistant Integration for IKEA OBEGRÄNSAD

[![hacs_badge](https://img.shields.io/badge/HACS-Custom-orange.svg)](https://github.com/custom-components/hacs)
[![Version](https://img.shields.io/badge/version-1.2.13-blue.svg)](https://github.com/Abrechen2/ikea-obegraensad-homeassistant/releases)

Home Assistant integration for the IKEA OBEGRÄNSAD LED matrix clock running the [IkeaObegraensad firmware](https://github.com/Abrechen2/IkeaObegraensad).

Communicates with the device over plain HTTP (local polling) and auto-discovers it via mDNS — no MQTT required.

## Features

- **Display on/off** — control the matrix from Home Assistant
- **Effect picker** — switch between all matrix effects (Snake, Clock, Rain, …, SensorClock)
- **Brightness** — 0–255 slider, also exposed as a Light entity
- **Auto-brightness** — automatic adjustment from the on-board LDR
- **Timezone** — set the clock's timezone
- **SensorClock** — display live temperature and humidity from HA sensors on the device
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

### Initial setup

1. Go to **Settings → Devices & Services → + Add Integration**
2. Search for **IKEA Obegraensad**
3. Enter the device's IP address (e.g. `192.168.1.100`)
4. Optional: change the port (default `80`) and give it a name
5. **SensorClock step (optional):** Select a temperature and humidity sensor from HA

### SensorClock — reconfigure sensors

To change the configured sensors after initial setup:

1. Go to **Settings → Devices & Services → IKEA Obegraensad**
2. Click the **⚙️ gear icon** on the entry
3. Select or change the temperature and humidity sensor entities

## Entities

After installation the following entities are created and grouped under one device:

| Type | Entity | Description |
|------|--------|-------------|
| Switch | Display | Display on/off |
| Switch | Auto Brightness | Toggle automatic brightness adjustment |
| Select | Effect | Pick the active effect (Snake, Clock, Rain, …, SensorClock) |
| Select | Timezone | Pick the device timezone |
| Light  | Brightness | Brightness control (also usable as a Light entity) |
| Number | Clock Slide Duration | How long the clock slide is shown (seconds) |
| Number | Temperature Slide Duration | How long the temperature slide is shown (seconds) |
| Number | Humidity Slide Duration | How long the humidity slide is shown (seconds) |
| Sensor | Time | Current time on the device |
| Sensor | Current Effect | Currently running effect |
| Sensor | Brightness | Current brightness value |
| Sensor | Sensor Value | Ambient light sensor reading |
| Sensor | IP Address | Device IP |
| Binary Sensor | Presence | Presence status (if used externally) |
| Binary Sensor | Display Status | Display power state |

## SensorClock

The **SensorClock** effect rotates between three slides:

1. Current time (clock)
2. Temperature (from a HA sensor)
3. Humidity (from a HA sensor)

### Setup

1. During initial integration setup, select your temperature and humidity sensor entities
2. Switch the effect to **sensorclock** via the Effect select entity
3. Adjust slide durations using the three **Number entities** (Clock / Temperature / Humidity Slide Duration)

The integration pushes sensor values to the device immediately on HA start and on every state change — no polling delay for sensor data.

### Change sensors after setup

Go to **Settings → Devices & Services → IKEA Obegraensad → ⚙️ gear icon**.

## Service: Configure auto-brightness

The service `ikea_obegraensad.configure_auto_brightness` exposes the advanced auto-brightness configuration:

```yaml
service: ikea_obegraensad.configure_auto_brightness
data:
  entity_id: switch.ikea_clock_auto_brightness
  enabled: true
  min: 50         # minimum brightness (0–1023)
  max: 800        # maximum brightness (0–1023)
  sensor_min: 100 # minimum sensor value (0–1024)
  sensor_max: 900 # maximum sensor value (0–1024)
```

## Automation examples

```yaml
automation:
  # Living room light on → display on
  - alias: "Living room light → display on"
    trigger:
      - platform: state
        entity_id: light.living_room
        to: "on"
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_display

  # Switch to SensorClock at sunrise
  - alias: "SensorClock at sunrise"
    trigger:
      - platform: sun
        event: sunrise
    action:
      - service: select.select_option
        target:
          entity_id: select.ikea_clock_effect
        data:
          option: "sensorclock"

  # Switch to plain clock effect every evening at 8 PM
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

  # Enable auto-brightness at sunset
  - alias: "Auto-brightness at sunset"
    trigger:
      - platform: sun
        event: sunset
    action:
      - service: switch.turn_on
        target:
          entity_id: switch.ikea_clock_auto_brightness
```

## Firmware requirements

The Arduino device must expose the following API endpoints:

| Endpoint | Description |
|----------|-------------|
| `GET /api/status` | Returns JSON status data |
| `GET /api/setDisplay?enabled=true\|false` | Display on/off |
| `GET /api/setBrightness?b=0-1023` | Set brightness |
| `GET /effect/{effect_name}` | Switch effect |
| `GET /api/setAutoBrightness?enabled=true\|false&min=…&max=…&sensorMin=…&sensorMax=…` | Configure auto-brightness |
| `GET /api/setTimezone?tz=Europe/Berlin` | Set timezone |
| `GET /api/setSensorData?temp=21.5&humi=55.0` | Push SensorClock values |
| `GET /api/setSlideConfig?clockDur=10&tempDur=5&humiDur=5` | Set slide durations |

Expected `/api/status` fields: `displayEnabled`, `brightness`, `currentEffect`, `time`, `presence`, `sensorValue`, `ipAddress`, `autoBrightnessEnabled`, `autoBrightnessMin`, `autoBrightnessMax`, `autoBrightnessSensorMin`, `autoBrightnessSensorMax`, `timezone`

The matching firmware lives in [Abrechen2/IkeaObegraensad](https://github.com/Abrechen2/IkeaObegraensad).

## Requirements

- Home Assistant 2023.1.0 or newer
- IKEA OBEGRÄNSAD device running the matching firmware

## Known limitations

- Status polling every 30 seconds (sensor push is event-driven and immediate)
- The timezone select contains the most common timezones (~25)
- SensorClock requires both temperature and humidity sensors to be configured — if only one is available, no data is pushed until the second sensor reports a value

## Support

Please open a GitHub issue at [Abrechen2/ikea-obegraensad-homeassistant/issues](https://github.com/Abrechen2/ikea-obegraensad-homeassistant/issues).
