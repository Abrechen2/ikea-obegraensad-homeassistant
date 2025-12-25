"""Sensor platform for Ikea Obegraensad integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.sensor import SensorEntity, SensorEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_TIME,
    KEY_CURRENT_EFFECT,
    KEY_BRIGHTNESS,
    KEY_SENSOR_VALUE,
    KEY_IP_ADDRESS,
)
from .coordinator import IkeaObegraensadDataUpdateCoordinator
from . import get_device_info

_LOGGER = logging.getLogger(__name__)

SENSOR_DESCRIPTIONS: tuple[SensorEntityDescription, ...] = (
    SensorEntityDescription(
        key=KEY_TIME,
        name="Time",
        icon="mdi:clock",
    ),
    SensorEntityDescription(
        key=KEY_CURRENT_EFFECT,
        name="Current Effect",
        icon="mdi:shape",
    ),
    SensorEntityDescription(
        key=KEY_BRIGHTNESS,
        name="Brightness",
        icon="mdi:brightness-6",
        native_unit_of_measurement="",
    ),
    SensorEntityDescription(
        key=KEY_SENSOR_VALUE,
        name="Sensor Value",
        icon="mdi:lightbulb-on",
        native_unit_of_measurement="",
    ),
    SensorEntityDescription(
        key=KEY_IP_ADDRESS,
        name="IP Address",
        icon="mdi:ip-network",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the sensor platform."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    entities = [
        IkeaObegraensadSensor(coordinator, entry, description)
        for description in SENSOR_DESCRIPTIONS
    ]
    
    async_add_entities(entities)


class IkeaObegraensadSensor(CoordinatorEntity, SensorEntity):
    """Representation of a Sensor."""

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
        description: SensorEntityDescription,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        base_name = entry.data.get("name", "Ikea Clock")
        self._attr_name = f"{base_name} {description.name}"
        self._attr_device_info = get_device_info(entry, coordinator)

    @property
    def native_value(self) -> str | int | None:
        """Return the native value of the sensor."""
        if self.coordinator.data is None:
            return None
        
        # Special handling for current effect sensor
        if self.entity_description.key == KEY_CURRENT_EFFECT:
            data = self.coordinator.data
            # Try multiple possible field names
            effect = (
                data.get(KEY_CURRENT_EFFECT) or
                data.get("effect") or
                data.get("activeEffect") or
                data.get("current_effect") or
                data.get("active_effect")
            )
            return effect if effect else None
        
        return self.coordinator.data.get(self.entity_description.key)

