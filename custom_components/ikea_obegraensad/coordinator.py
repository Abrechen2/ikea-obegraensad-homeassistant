"""DataUpdateCoordinator for Ikea Obegraensad."""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant, Event
from homeassistant.helpers.event import async_track_state_change_event
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp

from .const import (
    API_STATUS,
    API_SET_BRIGHTNESS,
    API_SET_AUTO_BRIGHTNESS,
    API_SET_TIMEZONE,
    API_EFFECT,
    API_SET_SENSOR_DATA,
    API_SET_SLIDE_CONFIG,
    CONF_TEMP_ENTITY,
    CONF_HUMI_ENTITY,
    CONF_CLOCK_DUR,
    CONF_TEMP_DUR,
    CONF_HUMI_DUR,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


async def decode_response_text(response: aiohttp.ClientResponse) -> str:
    """Decode response text with robust encoding handling.

    Tries multiple encodings to handle devices that may not send UTF-8.
    """
    # Read bytes first
    try:
        content_bytes = await response.read()
    except Exception as err:
        _LOGGER.debug("Error reading response bytes: %s, trying text() with error handling", err)
        # Fallback to text() with error handling
        try:
            return await response.text(encoding='utf-8', errors='replace')
        except Exception:
            # Last resort: try latin-1 (can decode any byte)
            return await response.text(encoding='latin-1')

    # Try different encodings
    encodings = ['utf-8', 'latin-1', 'cp1252', 'iso-8859-1']

    for encoding in encodings:
        try:
            text = content_bytes.decode(encoding)
            if encoding != 'utf-8':
                _LOGGER.debug("Decoded response using %s encoding", encoding)
            return text
        except UnicodeDecodeError:
            continue

    # If all encodings fail, use replace to handle invalid bytes
    _LOGGER.warning("Could not decode response with standard encodings, using utf-8 with error replacement")
    return content_bytes.decode('utf-8', errors='replace')


class IkeaObegraensadDataUpdateCoordinator(DataUpdateCoordinator):
    """Class to manage fetching data from the Ikea Obegraensad device."""

    def __init__(self, hass: HomeAssistant, host: str, port: int) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="Ikea Obegraensad",
            update_interval=timedelta(seconds=DEFAULT_SCAN_INTERVAL),
        )
        self.host = host
        self.port = port
        self.base_url = f"http://{host}:{port}"
        # SensorClock config (populated from config entry by async_setup_sensor_listeners)
        self._temp_entity: str | None = None
        self._humi_entity: str | None = None
        self._clock_dur: int = 10
        self._temp_dur: int = 5
        self._humi_dur: int = 5
        self._last_temp: float | None = None
        self._last_humi: float | None = None
        self._unsub_state_listener = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(f"{self.base_url}{API_STATUS}") as response:
                    if response.status == 200:
                        text = await decode_response_text(response)
                        data = json.loads(text)
                        return data
                    else:
                        raise UpdateFailed(f"HTTP {response.status}: {response.reason}")
        except aiohttp.ClientError as err:
            raise UpdateFailed(f"Error communicating with device: {err}") from err
        except Exception as err:
            raise UpdateFailed(f"Unexpected error: {err}") from err

    async def async_set_display(self, enabled: bool) -> bool:
        """Set display on/off."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(
                    f"{self.base_url}/api/setDisplay",
                    params={"enabled": "true" if enabled else "false"}
                ) as response:
                    if response.status == 200:
                        await self.async_request_refresh()
                        return True
                    else:
                        _LOGGER.error(f"Failed to set display: HTTP {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting display: {err}")
            return False

    async def async_set_brightness(self, brightness: int) -> bool:
        """Set brightness (0-1023)."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(
                    f"{self.base_url}{API_SET_BRIGHTNESS}",
                    params={"b": str(brightness)}
                ) as response:
                    if response.status == 200:
                        await self.async_request_refresh()
                        return True
                    else:
                        _LOGGER.error(f"Failed to set brightness: HTTP {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting brightness: {err}")
            return False

    async def async_set_effect(self, effect_name: str) -> bool:
        """Set effect by name."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(
                    f"{self.base_url}{API_EFFECT}/{effect_name}"
                ) as response:
                    if response.status == 200:
                        await self.async_request_refresh()
                        return True
                    else:
                        _LOGGER.error(f"Failed to set effect: HTTP {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting effect: {err}")
            return False

    async def async_set_auto_brightness(
        self,
        enabled: bool,
        min_brightness: int | None = None,
        max_brightness: int | None = None,
        sensor_min: int | None = None,
        sensor_max: int | None = None,
    ) -> bool:
        """Set auto-brightness on/off with optional configuration."""
        try:
            params: dict[str, str] = {"enabled": "true" if enabled else "false"}

            # Only add parameters that are provided
            if min_brightness is not None:
                params["min"] = str(min_brightness)
            if max_brightness is not None:
                params["max"] = str(max_brightness)
            if sensor_min is not None:
                params["sensorMin"] = str(sensor_min)
            if sensor_max is not None:
                params["sensorMax"] = str(sensor_max)

            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(
                    f"{self.base_url}{API_SET_AUTO_BRIGHTNESS}",
                    params=params
                ) as response:
                    if response.status == 200:
                        await self.async_request_refresh()
                        return True
                    else:
                        _LOGGER.error(f"Failed to set auto-brightness: HTTP {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting auto-brightness: {err}")
            return False

    async def async_set_timezone(self, timezone: str) -> bool:
        """Set timezone."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(
                    f"{self.base_url}{API_SET_TIMEZONE}",
                    params={"tz": timezone}
                ) as response:
                    if response.status == 200:
                        await self.async_request_refresh()
                        return True
                    else:
                        _LOGGER.error(f"Failed to set timezone: HTTP {response.status}")
                        return False
        except Exception as err:
            _LOGGER.error(f"Error setting timezone: {err}")
            return False

    async def async_setup_sensor_listeners(self, hass, config: dict) -> None:
        """Set up state listeners for temperature and humidity entities.

        Call this on initial setup and whenever options change.
        config: dict with keys temp_entity, humi_entity, clock_duration,
                temp_duration, humi_duration.
        """
        # Unsubscribe previous listener to avoid duplicates
        if self._unsub_state_listener is not None:
            self._unsub_state_listener()
            self._unsub_state_listener = None

        self._temp_entity = config.get(CONF_TEMP_ENTITY) or None
        self._humi_entity = config.get(CONF_HUMI_ENTITY) or None
        self._clock_dur   = int(config.get(CONF_CLOCK_DUR, 10))
        self._temp_dur    = int(config.get(CONF_TEMP_DUR,  5))
        self._humi_dur    = int(config.get(CONF_HUMI_DUR,  5))

        # Sync slide durations to device
        await self.async_set_slide_config()

        if not self._temp_entity and not self._humi_entity:
            return  # no entities configured, nothing to listen to

        entity_ids = [e for e in [self._temp_entity, self._humi_entity] if e]
        self._unsub_state_listener = async_track_state_change_event(
            hass, entity_ids, self._on_sensor_state_change
        )
        _LOGGER.debug("SensorClock: listening to %s", entity_ids)

    async def _on_sensor_state_change(self, event: Event) -> None:
        """Handle state changes from temperature or humidity entities."""
        entity_id = event.data.get("entity_id")
        new_state  = event.data.get("new_state")

        if new_state is None or new_state.state in ("unavailable", "unknown", ""):
            _LOGGER.warning("SensorClock: %s is %s, skipping push",
                            entity_id, new_state.state if new_state else "None")
            return

        try:
            value = float(new_state.state)
        except (ValueError, TypeError):
            _LOGGER.warning("SensorClock: %s state '%s' is not a float, skipping",
                            entity_id, new_state.state)
            return

        if entity_id == self._temp_entity:
            self._last_temp = value
        elif entity_id == self._humi_entity:
            self._last_humi = value

        # Only push when both values are known
        if self._last_temp is None or self._last_humi is None:
            _LOGGER.debug("SensorClock: waiting for both sensors (%s=%s, %s=%s)",
                          self._temp_entity, self._last_temp,
                          self._humi_entity, self._last_humi)
            return

        await self.async_push_sensor_data(self._last_temp, self._last_humi)

    async def async_push_sensor_data(self, temp: float, humi: float) -> bool:
        """Push temperature and humidity values to the device."""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            ) as session:
                params = {"temp": f"{temp:.1f}", "humi": f"{humi:.1f}"}
                async with session.get(
                    f"{self.base_url}{API_SET_SENSOR_DATA}", params=params
                ) as response:
                    if response.status == 200:
                        return True
                    _LOGGER.warning(
                        "SensorClock: setSensorData returned HTTP %s", response.status
                    )
                    return False
        except Exception as err:
            _LOGGER.warning("SensorClock: error pushing sensor data: %s", err)
            return False

    async def async_set_slide_config(self) -> bool:
        """Push slide duration config to the device."""
        try:
            async with aiohttp.ClientSession(
                timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)
            ) as session:
                params = {
                    "clockDur": str(self._clock_dur),
                    "tempDur":  str(self._temp_dur),
                    "humiDur":  str(self._humi_dur),
                }
                async with session.get(
                    f"{self.base_url}{API_SET_SLIDE_CONFIG}", params=params
                ) as response:
                    if response.status == 200:
                        return True
                    _LOGGER.warning(
                        "SensorClock: setSlideConfig returned HTTP %s", response.status
                    )
                    return False
        except Exception as err:
            _LOGGER.warning("SensorClock: error setting slide config: %s", err)
            return False
