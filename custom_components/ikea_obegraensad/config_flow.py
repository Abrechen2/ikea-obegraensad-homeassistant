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
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_TIMEOUT, API_STATUS

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Optional(CONF_PORT, default=DEFAULT_PORT): cv.port,
        vol.Optional(CONF_NAME, default="Ikea Clock"): str,
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
                
                text = await response.text()
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

    VERSION = 1

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
            
            # Check if unique ID is already configured
            # _abort_if_unique_id_configured() will raise AbortFlow if already configured
            # This will automatically abort the flow, so we don't need to catch it
            self._abort_if_unique_id_configured()
            _LOGGER.debug("Unique ID %s is not yet configured, proceeding with entry creation", unique_id)
            
            _LOGGER.info("Creating config entry for device at %s:%s with title: %s", user_input[CONF_HOST], user_input.get(CONF_PORT, DEFAULT_PORT), info["title"])
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

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
        
        # Check if unique ID is already configured
        # _abort_if_unique_id_configured() will raise AbortFlow if already configured
        # This will automatically abort the flow, so we don't need to catch it
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


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""

