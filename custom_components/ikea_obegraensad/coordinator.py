"""DataUpdateCoordinator for Ikea Obegraensad."""
from __future__ import annotations

import json
import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
import aiohttp

from .const import (
    API_STATUS,
    API_SET_BRIGHTNESS,
    API_SET_AUTO_BRIGHTNESS,
    API_SET_TIMEZONE,
    API_EFFECT,
    DEFAULT_TIMEOUT,
    DEFAULT_SCAN_INTERVAL,
)

_LOGGER = logging.getLogger(__name__)


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

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the device."""
        try:
            async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
                async with session.get(f"{self.base_url}{API_STATUS}") as response:
                    if response.status == 200:
                        text = await response.text()
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

