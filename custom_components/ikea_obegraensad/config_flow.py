"""Config flow for Ikea Obegraensad integration."""
from __future__ import annotations

import asyncio
import json
import logging
from typing import Any

import aiohttp
import voluptuous as vol

from homeassistant import config_entries
from homeassistant.components import zeroconf
from homeassistant.const import CONF_HOST, CONF_PORT, CONF_NAME
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.selector import (
    BooleanSelector,
    EntitySelector,
    EntitySelectorConfig,
    NumberSelector,
    NumberSelectorConfig,
    NumberSelectorMode,
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import (
    DOMAIN, DEFAULT_PORT, DEFAULT_TIMEOUT, API_STATUS,
    CONF_TEMP_ENTITY, CONF_HUMI_ENTITY,
    CONF_CLOCK_DUR, CONF_TEMP_DUR, CONF_HUMI_DUR,
    CONF_DISPLAY_ENABLED, CONF_AUTO_BRIGHTNESS, CONF_TIMEZONE_OPT,
    TIMEZONES, KEY_DISPLAY_ENABLED, KEY_AUTO_BRIGHTNESS_ENABLED, KEY_TIMEZONE,
)

_LOGGER = logging.getLogger(__name__)


async def decode_response_text(response: aiohttp.ClientResponse) -> str:
    """Decode response text with robust encoding handling (async version).

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


STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_NAME, default="Ikea Clock"): str,
    }
)

STEP_SENSOR_SCHEMA = vol.Schema(
    {
        vol.Optional(CONF_TEMP_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(CONF_HUMI_ENTITY): EntitySelector(
            EntitySelectorConfig(domain="sensor")
        ),
        vol.Optional(CONF_CLOCK_DUR, default=10): NumberSelector(
            NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_TEMP_DUR, default=5): NumberSelector(
            NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)
        ),
        vol.Optional(CONF_HUMI_DUR, default=5): NumberSelector(
            NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)
        ),
    }
)


async def validate_input(data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    host = data[CONF_HOST]
    port = data.get(CONF_PORT, DEFAULT_PORT)
    url = f"http://{host}:{port}{API_STATUS}"

    _LOGGER.debug("Validating connection to %s", url)

    try:
        async with aiohttp.ClientSession(timeout=aiohttp.ClientTimeout(total=DEFAULT_TIMEOUT)) as session:
            async with session.get(url) as response:
                _LOGGER.debug("Response status: %s, Content-Type: %s", response.status, response.content_type)

                if response.status != 200:
                    _LOGGER.warning("HTTP error %s from %s (reason: %s)", response.status, url, response.reason)
                    raise CannotConnect(f"HTTP {response.status}: {response.reason}")

                text = await decode_response_text(response)
                _LOGGER.debug("Response text length: %d characters", len(text))

                if not text:
                    _LOGGER.error("Empty response from %s", url)
                    raise CannotConnect("Empty response from device")

                try:
                    result = json.loads(text)
                except json.JSONDecodeError as err:
                    _LOGGER.error("Invalid JSON response from %s: %s. Response: %s", url, err, text[:200])
                    raise CannotConnect from err

                # Log full API response for debugging (first 500 characters)
                _LOGGER.debug("API response from %s (first 500 chars): %s", url, text[:500])
                _LOGGER.debug("Parsed JSON keys: %s", list(result.keys()) if isinstance(result, dict) else "Not a dict")

                _LOGGER.debug("Successfully validated connection to %s", url)
                return {"title": data.get(CONF_NAME, "Ikea Clock"), "device_info": result}

    except asyncio.TimeoutError as err:
        _LOGGER.error("Timeout connecting to %s (timeout: %s seconds)", url, DEFAULT_TIMEOUT)
        raise CannotConnect(f"Connection timeout after {DEFAULT_TIMEOUT} seconds") from err
    except aiohttp.ClientError as err:
        _LOGGER.error("Client error connecting to %s: %s", url, err)
        raise CannotConnect(f"Connection error: {err}") from err


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Ikea Obegraensad."""

    VERSION = 2

    def __init__(self):
        self._user_data: dict[str, Any] = {}

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            _LOGGER.info("Starting validation for device at %s:%s", user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT))
            info = await validate_input(user_input)
        except CannotConnect as err:
            _LOGGER.warning("Cannot connect to device at %s:%s: %s", user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT), err)
            errors["base"] = "cannot_connect"
        except Exception as err:
            _LOGGER.exception("Unexpected exception while validating device at %s:%s: %s", user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT), err)
            errors["base"] = "unknown"
        else:
            unique_id = f"{user_input[CONF_HOST]}:{user_input.get(CONF_PORT, DEFAULT_PORT)}"
            _LOGGER.info("Validation successful. Setting unique_id: %s", unique_id)
            await self.async_set_unique_id(unique_id)
            self._abort_if_unique_id_configured()
            _LOGGER.debug("Unique ID %s is not yet configured, proceeding with entry creation", unique_id)

            _LOGGER.info("Creating config entry for device at %s:%s with title: %s", user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT), info["title"])
            # Store host/port/name and proceed to sensor config step
            self._user_data = user_input
            return await self.async_step_sensor()

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    async def async_step_sensor(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle optional sensor entity configuration step."""
        if user_input is None:
            return self.async_show_form(
                step_id="sensor", data_schema=STEP_SENSOR_SCHEMA
            )

        # Merge sensor config into user data and create entry
        combined = {**self._user_data, **user_input}
        return self.async_create_entry(title=self._user_data.get(CONF_NAME, "Ikea Clock"), data=combined)

    @staticmethod
    @callback
    def async_get_options_flow(config_entry):
        return OptionsFlowHandler()

    async def async_step_zeroconf(
        self, discovery_info: zeroconf.ZeroconfServiceInfo
    ) -> FlowResult:
        """Handle zeroconf discovery."""
        host = discovery_info.host
        port = discovery_info.port or DEFAULT_PORT
        hostname = discovery_info.hostname.lower()

        # Check if hostname contains "ikea" or "clock" to identify the device
        if "ikea" not in hostname and "clock" not in hostname:
            _LOGGER.debug("Zeroconf discovery: Hostname '%s' does not contain 'ikea' or 'clock', aborting", hostname)
            return self.async_abort(reason="not_ikea_clock")

        # Check if already configured
        unique_id = f"{host}:{port}"
        _LOGGER.info("Zeroconf discovery: Found device at %s:%s (hostname: %s). Setting unique_id: %s", host, port, hostname, unique_id)
        await self.async_set_unique_id(unique_id)
        self._abort_if_unique_id_configured()
        _LOGGER.debug("Zeroconf: Unique ID %s is not yet configured, proceeding", unique_id)

        # Pre-fill the form with discovered data
        self.context.update({"title_placeholders": {"name": "Ikea Clock"}})
        return await self.async_step_user(
            {
                CONF_HOST: host,
                CONF_PORT: port,
                CONF_NAME: "Ikea Clock",
            }
        )


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options for device settings and SensorClock configuration."""

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Show options form pre-filled with current values."""
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)

        current = {**self.config_entry.data, **self.config_entry.options}

        # Get live device state for display/brightness/timezone defaults
        coordinator = self.hass.data.get(DOMAIN, {}).get(self.config_entry.entry_id)
        device_data = coordinator.data if coordinator and coordinator.data else {}

        schema = vol.Schema(
            {
                # Device settings
                vol.Optional(CONF_DISPLAY_ENABLED): BooleanSelector(),
                vol.Optional(CONF_AUTO_BRIGHTNESS): BooleanSelector(),
                vol.Optional(CONF_TIMEZONE_OPT): SelectSelector(
                    SelectSelectorConfig(options=TIMEZONES, mode=SelectSelectorMode.DROPDOWN)
                ),
                # SensorClock
                vol.Optional(CONF_TEMP_ENTITY): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(CONF_HUMI_ENTITY): EntitySelector(EntitySelectorConfig(domain="sensor")),
                vol.Optional(CONF_CLOCK_DUR): NumberSelector(NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)),
                vol.Optional(CONF_TEMP_DUR): NumberSelector(NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)),
                vol.Optional(CONF_HUMI_DUR): NumberSelector(NumberSelectorConfig(min=1, max=3600, step=1, mode=NumberSelectorMode.BOX)),
            }
        )

        suggested = {
            CONF_DISPLAY_ENABLED: current.get(CONF_DISPLAY_ENABLED, device_data.get(KEY_DISPLAY_ENABLED, True)),
            CONF_AUTO_BRIGHTNESS: current.get(CONF_AUTO_BRIGHTNESS, device_data.get(KEY_AUTO_BRIGHTNESS_ENABLED, False)),
            CONF_TIMEZONE_OPT: current.get(CONF_TIMEZONE_OPT, device_data.get(KEY_TIMEZONE, "Europe/Berlin")),
            CONF_CLOCK_DUR: int(current.get(CONF_CLOCK_DUR, 10)),
            CONF_TEMP_DUR: int(current.get(CONF_TEMP_DUR, 5)),
            CONF_HUMI_DUR: int(current.get(CONF_HUMI_DUR, 5)),
        }
        if current.get(CONF_TEMP_ENTITY):
            suggested[CONF_TEMP_ENTITY] = current[CONF_TEMP_ENTITY]
        if current.get(CONF_HUMI_ENTITY):
            suggested[CONF_HUMI_ENTITY] = current[CONF_HUMI_ENTITY]

        return self.async_show_form(
            step_id="init",
            data_schema=self.add_suggested_values_to_schema(schema, suggested),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
