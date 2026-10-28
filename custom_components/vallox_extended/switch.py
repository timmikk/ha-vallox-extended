"""Switch platform for Vallox Extended."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity


class ValloxExtendedBypassLockedSwitch(ValloxExtendedEntity, SwitchEntity):
    """Switch to lock or unlock the bypass damper."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ValloxExtendedCoordinator) -> None:
        super().__init__(coordinator, "bypass_locked")
        self._attr_name = "Bypass locked"

    @property
    def is_on(self) -> bool:
        return self.coordinator.data.get("A_CYC_BYPASS_LOCKED") == 1

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_values({"A_CYC_BYPASS_LOCKED": 1})
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_values({"A_CYC_BYPASS_LOCKED": 0})
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vallox Extended switch entities."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    async_add_entities([ValloxExtendedBypassLockedSwitch(coordinator)])
