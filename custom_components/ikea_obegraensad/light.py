"""Light platform for Ikea Obegraensad integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    LightEntity,
    ColorMode,
    ATTR_BRIGHTNESS,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    DOMAIN,
    KEY_DISPLAY_ENABLED,
    KEY_BRIGHTNESS,
    BRIGHTNESS_MAX_API,
    BRIGHTNESS_MAX_HA,
)
from .coordinator import IkeaObegraensadDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the light platform."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([IkeaObegraensadLight(coordinator, entry)])


class IkeaObegraensadLight(CoordinatorEntity, LightEntity):
    """Representation of a Light (Brightness Control)."""

    _attr_color_mode = ColorMode.BRIGHTNESS
    _attr_supported_color_modes = {ColorMode.BRIGHTNESS}

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_light"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} Brightness"
        self._attr_icon = "mdi:brightness-6"

    @property
    def is_on(self) -> bool | None:
        """Return true if the light is on."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(KEY_DISPLAY_ENABLED, False)

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the light (0-255)."""
        if self.coordinator.data is None:
            return None
        api_brightness = self.coordinator.data.get(KEY_BRIGHTNESS, 0)
        # Convert from API range (0-1023) to HA range (0-255)
        if api_brightness is None:
            return None
        return int((api_brightness / BRIGHTNESS_MAX_API) * BRIGHTNESS_MAX_HA)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the light."""
        brightness = kwargs.get(ATTR_BRIGHTNESS)
        
        # If brightness is provided, set it
        if brightness is not None:
            # Convert from HA range (0-255) to API range (0-1023)
            api_brightness = int((brightness / BRIGHTNESS_MAX_HA) * BRIGHTNESS_MAX_API)
            success = await self.coordinator.async_set_brightness(api_brightness)
            if not success:
                _LOGGER.error("Failed to set brightness")
        
        # Turn on display if not already on
        if not self.is_on:
            success = await self.coordinator.async_set_display(True)
            if not success:
                _LOGGER.error("Failed to turn on display")

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the light."""
        success = await self.coordinator.async_set_display(False)
        if not success:
            _LOGGER.error("Failed to turn off display")

