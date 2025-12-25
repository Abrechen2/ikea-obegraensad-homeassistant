"""Diagnostics support for Ikea Obegraensad integration."""
from __future__ import annotations

from typing import Any

from homeassistant.components.diagnostics import async_redact_data
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant

from .const import DOMAIN
from .coordinator import IkeaObegraensadDataUpdateCoordinator

TO_REDACT = {
    "password",
    "token",
    "api_key",
}


async def async_get_config_entry_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry
) -> dict[str, Any]:
    """Return diagnostics for a config entry."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    return {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
            "options": async_redact_data(entry.options, TO_REDACT),
            "pref_disable_new_entities": entry.pref_disable_new_entities,
            "pref_disable_polling": entry.pref_disable_polling,
            "source": entry.source,
            "unique_id": entry.unique_id,
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_time": coordinator.last_update_time.isoformat() if coordinator.last_update_time else None,
            "update_interval": str(coordinator.update_interval),
        },
        "device": {
            "host": coordinator.host,
            "port": coordinator.port,
            "base_url": coordinator.base_url,
        },
    }


async def async_get_device_diagnostics(
    hass: HomeAssistant, entry: ConfigEntry, device: Any
) -> dict[str, Any]:
    """Return diagnostics for a device."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    diagnostics_data: dict[str, Any] = {
        "config_entry": {
            "entry_id": entry.entry_id,
            "version": entry.version,
            "domain": entry.domain,
            "title": entry.title,
            "data": async_redact_data(entry.data, TO_REDACT),
        },
        "coordinator": {
            "last_update_success": coordinator.last_update_success,
            "last_update_time": coordinator.last_update_time.isoformat() if coordinator.last_update_time else None,
            "update_interval": str(coordinator.update_interval),
        },
        "device": {
            "host": coordinator.host,
            "port": coordinator.port,
            "base_url": coordinator.base_url,
        },
        "status": coordinator.data if coordinator.data else {},
    }
    
    return diagnostics_data

