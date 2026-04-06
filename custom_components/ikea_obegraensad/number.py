"""Number platform for Ikea Obegraensad — SensorClock slide durations."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from typing import Any

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, CONF_CLOCK_DUR, CONF_TEMP_DUR, CONF_HUMI_DUR
from .coordinator import IkeaObegraensadDataUpdateCoordinator
from . import get_device_info

_LOGGER = logging.getLogger(__name__)


@dataclass
class IkeaDurationDescription(NumberEntityDescription):
    coordinator_attr: str = ""
    config_key: str = ""


DURATION_DESCRIPTIONS: tuple[IkeaDurationDescription, ...] = (
    IkeaDurationDescription(
        key="clock_duration",
        name="Clock Slide Duration",
        icon="mdi:clock-outline",
        native_min_value=1,
        native_max_value=3600,
        native_step=1,
        native_unit_of_measurement="s",
        mode=NumberMode.BOX,
        coordinator_attr="_clock_dur",
        config_key=CONF_CLOCK_DUR,
    ),
    IkeaDurationDescription(
        key="temp_duration",
        name="Temperature Slide Duration",
        icon="mdi:thermometer",
        native_min_value=1,
        native_max_value=3600,
        native_step=1,
        native_unit_of_measurement="s",
        mode=NumberMode.BOX,
        coordinator_attr="_temp_dur",
        config_key=CONF_TEMP_DUR,
    ),
    IkeaDurationDescription(
        key="humi_duration",
        name="Humidity Slide Duration",
        icon="mdi:water-percent",
        native_min_value=1,
        native_max_value=3600,
        native_step=1,
        native_unit_of_measurement="s",
        mode=NumberMode.BOX,
        coordinator_attr="_humi_dur",
        config_key=CONF_HUMI_DUR,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up number entities for SensorClock durations."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        IkeaObegraensadDurationNumber(coordinator, entry, desc)
        for desc in DURATION_DESCRIPTIONS
    )


class IkeaObegraensadDurationNumber(CoordinatorEntity, NumberEntity):
    """Number entity for a SensorClock slide duration."""

    entity_description: IkeaDurationDescription

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
        description: IkeaDurationDescription,
    ) -> None:
        super().__init__(coordinator)
        self.entity_description = description
        self._attr_unique_id = f"{entry.entry_id}_{description.key}"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} {description.name}"
        self._attr_device_info = get_device_info(entry, coordinator)

    @property
    def native_value(self) -> float:
        return float(getattr(self.coordinator, self.entity_description.coordinator_attr, 10))

    async def async_set_native_value(self, value: float) -> None:
        setattr(self.coordinator, self.entity_description.coordinator_attr, int(value))
        await self.coordinator.async_set_slide_config()
        self.async_write_ha_state()
