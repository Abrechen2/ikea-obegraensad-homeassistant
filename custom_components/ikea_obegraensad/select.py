"""Select platform for Ikea Obegraensad integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, EFFECTS, KEY_CURRENT_EFFECT, TIMEZONES, KEY_TIMEZONE
from .coordinator import IkeaObegraensadDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the select platform."""
    coordinator: IkeaObegraensadDataUpdateCoordinator = hass.data[DOMAIN][entry.entry_id]
    
    async_add_entities([
        IkeaObegraensadEffectSelect(coordinator, entry),
        IkeaObegraensadTimezoneSelect(coordinator, entry),
    ])


class IkeaObegraensadEffectSelect(CoordinatorEntity, SelectEntity):
    """Representation of an Effect Select."""

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_effect"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} Effect"
        self._attr_icon = "mdi:shape"
        self._attr_options = EFFECTS

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data is None:
            return None
        return self.coordinator.data.get(KEY_CURRENT_EFFECT)

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        success = await self.coordinator.async_set_effect(option)
        if not success:
            _LOGGER.error(f"Failed to set effect to {option}")


class IkeaObegraensadTimezoneSelect(CoordinatorEntity, SelectEntity):
    """Representation of a Timezone Select."""

    def __init__(
        self,
        coordinator: IkeaObegraensadDataUpdateCoordinator,
        entry: ConfigEntry,
    ) -> None:
        """Initialize the timezone select."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_timezone"
        self._attr_name = f"{entry.data.get('name', 'Ikea Clock')} Timezone"
        self._attr_icon = "mdi:clock-time-three"
        self._attr_options = list(TIMEZONES)

    @property
    def current_option(self) -> str | None:
        """Return the current selected option."""
        if self.coordinator.data is None:
            return None
        timezone = self.coordinator.data.get(KEY_TIMEZONE)
        # If timezone is not in options, return first option (UTC) as default
        if timezone and timezone in self._attr_options:
            return timezone
        return None

    async def async_select_option(self, option: str) -> None:
        """Change the selected option."""
        success = await self.coordinator.async_set_timezone(option)
        if not success:
            _LOGGER.error(f"Failed to set timezone to {option}")

