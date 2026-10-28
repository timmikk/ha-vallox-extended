"""Date platform for Vallox Extended."""

from __future__ import annotations

from datetime import date

from homeassistant.components.date import DateEntity
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity


class ValloxExtendedFilterChangeDate(ValloxExtendedEntity, DateEntity):
    """Representation of the Vallox filter change date entity."""

    _attr_entity_category = EntityCategory.CONFIG

    def __init__(self, coordinator: ValloxExtendedCoordinator) -> None:
        super().__init__(coordinator, "filter_change_date")
        self._attr_name = "Filter change date"

    @property
    def native_value(self) -> date | None:
        return self.coordinator.data.metric_data.filter_change_date

    async def async_set_value(self, value: date) -> None:
        await self.coordinator.client.set_filter_change_date(value)
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vallox Extended date entities."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    async_add_entities([ValloxExtendedFilterChangeDate(coordinator)])
