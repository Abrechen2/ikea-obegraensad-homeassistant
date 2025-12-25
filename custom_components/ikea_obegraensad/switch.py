"""Switch platform for Ikea Obegraensad integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, KEY_AUTO_BRIGHTNESS_ENABLED
from .coordinator import IkeaObegraensadDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the switch platform."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        IkeaObegraensadDisplaySwitch(coordinator, entry),
        IkeaObegraensadAutoBrightnessSwitch(coordinator, entry),
    ])


class IkeaObegraensadDisplaySwitch(CoordinatorEntity, SwitchEntity):
    """Representation of a Display Switch."""

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_display"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} Display"
        self._attr_icon = "mdi:led-on"

    @property
    def is_on(self) -> bool | None:
        """Return true if the display is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get("displayEnabled", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the display."""
        success = await self.coordinator.async_set_display(True)
        if not success:
            _LOGGER.error("Failed to turn on display")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the display."""
        success = await self.coordinator.async_set_display(False)
        if not success:
            _LOGGER.error("Failed to turn off display")


class IkeaObegraensadAutoBrightnessSwitch(CoordinatorEntity, SwitchEntity):
    """Representation of an Auto-Brightness Switch."""

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the auto-brightness switch."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_auto_brightness"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} Auto Brightness"
        self._attr_icon = "mdi:brightness-auto"

    @property
    def is_on(self) -> bool | None:
        """Return true if auto-brightness is enabled."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(KEY_AUTO_BRIGHTNESS_ENABLED, False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on auto-brightness."""
        success = await self.coordinator.async_set_auto_brightness(True)
        if not success:
            _LOGGER.error("Failed to turn on auto-brightness")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off auto-brightness."""
        success = await self.coordinator.async_set_auto_brightness(False)
        if not success:
            _LOGGER.error("Failed to turn off auto-brightness")

