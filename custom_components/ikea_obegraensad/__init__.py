"""The Ikea Obegraensad integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_PORT, Platform, ATTR_ENTITY_ID
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers import entity_registry as er

from .const import DOMAIN, DEFAULT_PORT, DEFAULT_TIMEOUT, BRIGHTNESS_MAX_API
from .coordinator import IkeaObegraensadDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


def get_device_info(entry: ConfigEntry, coordinator: IkeaObegraensadDataUpdateCoordinator) -> dict[str, Any]:
    """Get device info for entities."""
    host = entry.data.get("host", "")
    port = entry.data.get("port", DEFAULT_PORT)
    
    # Try to get firmware version from coordinator data
    # Check multiple possible field names
    sw_version = "Unknown"
    if coordinator.data:
        # Try various possible field names for firmware version
        sw_version = (
            coordinator.data.get("firmwareVersion") or
            coordinator.data.get("firmware") or
            coordinator.data.get("version") or
            coordinator.data.get("sw_version") or
            coordinator.data.get("fw_version") or
            "Unknown"
        )
        # Log available keys for debugging if firmware not found
        if sw_version == "Unknown" and _LOGGER.isEnabledFor(logging.DEBUG):
            _LOGGER.debug("Firmware not found in API response. Available keys: %s", list(coordinator.data.keys()))
    
    return {
        "identifiers": {(DOMAIN, entry.entry_id)},
        "name": entry.data.get("name", "Ikea Clock"),
        "manufacturer": "Abrechen2",
        "model": "Obegraensad",
        "sw_version": sw_version,
        "configuration_url": f"http://{host}:{port}",
    }

PLATFORMS: list[Platform] = [
    Platform.SWITCH,
    Platform.SELECT,
    Platform.LIGHT,
    Platform.SENSOR,
    Platform.BINARY_SENSOR,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Ikea Obegraensad from a config entry."""
    host = entry.data[CONF_HOST]
    port = entry.data.get(CONF_PORT, DEFAULT_PORT)
    
    coordinator = IkeaObegraensadDataUpdateCoordinator(hass, host, port)
    
    try:
        await coordinator.async_config_entry_first_refresh()
    except Exception as err:
        raise ConfigEntryNotReady(f"Error connecting to device: {err}") from err
    
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator
    
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    
    # Register service for auto-brightness configuration
    if not hass.services.has_service(DOMAIN, "configure_auto_brightness"):
        async def async_handle_configure_auto_brightness(call: ServiceCall) -> None:
            """Handle configure_auto_brightness service call."""
            entity_ids = call.data[ATTR_ENTITY_ID]
            if isinstance(entity_ids, str):
                entity_ids = [entity_ids]
            
            registry = er.async_get(hass)
            coordinator_found = None
            
            # Find coordinator for the entity
            for entity_id in entity_ids:
                if entity := registry.async_get(entity_id):
                    # Get the config entry ID from the entity
                    if entity.config_entry_id and entity.config_entry_id in hass.data.get(DOMAIN, {}):
                        coord = hass.data[DOMAIN][entity.config_entry_id]
                        if isinstance(coord, IkeaObegraensadDataUpdateCoordinator):
                            coordinator_found = coord
                            break
            
            if coordinator_found is None:
                _LOGGER.error(f"Could not find coordinator for entity {entity_ids}")
                return
            
            enabled = call.data.get("enabled")
            min_brightness = call.data.get("min")
            max_brightness = call.data.get("max")
            sensor_min = call.data.get("sensor_min")
            sensor_max = call.data.get("sensor_max")
            
            # Validate brightness values (schema already validates, but double-check)
            if min_brightness is not None and (min_brightness < 0 or min_brightness > BRIGHTNESS_MAX_API):
                _LOGGER.error(f"min_brightness must be between 0 and {BRIGHTNESS_MAX_API}")
                return
            if max_brightness is not None and (max_brightness < 0 or max_brightness > BRIGHTNESS_MAX_API):
                _LOGGER.error(f"max_brightness must be between 0 and {BRIGHTNESS_MAX_API}")
                return
            if sensor_min is not None and (sensor_min < 0 or sensor_min > 1024):
                _LOGGER.error("sensor_min must be between 0 and 1024")
                return
            if sensor_max is not None and (sensor_max < 0 or sensor_max > 1024):
                _LOGGER.error("sensor_max must be between 0 and 1024")
                return
            
            # Call coordinator method - only enabled if explicitly provided
            if enabled is not None:
                await coordinator_found.async_set_auto_brightness(
                    enabled=enabled,
                    min_brightness=min_brightness,
                    max_brightness=max_brightness,
                    sensor_min=sensor_min,
                    sensor_max=sensor_max,
                )
            else:
                # Get current enabled state from coordinator data
                current_enabled = True
                if coordinator_found.data:
                    current_enabled = coordinator_found.data.get("autoBrightnessEnabled", True)
                
                await coordinator_found.async_set_auto_brightness(
                    enabled=current_enabled,
                    min_brightness=min_brightness,
                    max_brightness=max_brightness,
                    sensor_min=sensor_min,
                    sensor_max=sensor_max,
                )
        
        hass.services.async_register(
            DOMAIN,
            "configure_auto_brightness",
            async_handle_configure_auto_brightness,
            schema=vol.Schema({
                vol.Required(ATTR_ENTITY_ID): cv.entity_id,
                vol.Optional("enabled"): cv.boolean,
                vol.Optional("min"): vol.All(vol.Coerce(int), vol.Range(min=0, max=BRIGHTNESS_MAX_API)),
                vol.Optional("max"): vol.All(vol.Coerce(int), vol.Range(min=0, max=BRIGHTNESS_MAX_API)),
                vol.Optional("sensor_min"): vol.All(vol.Coerce(int), vol.Range(min=0, max=1024)),
                vol.Optional("sensor_max"): vol.All(vol.Coerce(int), vol.Range(min=0, max=1024)),
            }),
        )
    
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)
    
    # Unregister service if no entries left
    if not hass.data.get(DOMAIN):
        hass.services.async_remove(DOMAIN, "configure_auto_brightness")
    
    return unload_ok

