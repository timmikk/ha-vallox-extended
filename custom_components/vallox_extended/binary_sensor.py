"""Read-only Vallox Extended binary sensors."""

from __future__ import annotations

from typing import Any

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
)
from homeassistant.const import EntityCategory
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CELL_STATE_BYPASS, CELL_STATE_DEFROSTING
from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity


class ValloxExtendedBinarySensor(ValloxExtendedEntity, BinarySensorEntity):
    """A binary sensor derived from a documented read-only metric."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(
        self,
        coordinator: ValloxExtendedCoordinator,
        key: str,
        name: str,
        metric: str,
        expected: int,
        valid_values: frozenset[int],
    ) -> None:
        super().__init__(coordinator, key)
        self._attr_name = name
        self._metric = metric
        self._expected = expected
        self._valid_values = valid_values

    @property
    def is_on(self) -> bool | None:
        value = self.coordinator.data.get(self._metric)
        return value == self._expected if value in self._valid_values else None


class ValloxExtendedFaultActiveBinarySensor(ValloxExtendedBinarySensor):
    """Fault active binary sensor with detailed alarm attributes."""

    _attr_device_class = BinarySensorDeviceClass.PROBLEM

    def __init__(
        self,
        coordinator: ValloxExtendedCoordinator,
    ) -> None:
        super().__init__(
            coordinator,
            "fault_active",
            "Fault active",
            "A_CYC_FAULT_ACTIVITY",
            1,
            frozenset({0, 1}),
        )

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        try:
            alarms = self.coordinator.data.metric_data.get_alarms(skip_solved=True)
            return {
                "active_alarms": [
                    {
                        "nr": a.nr,
                        "code": a.code,
                        "message": getattr(a, "message", None),
                        "severity": a.severity.name if a.severity else None,
                        "first_date": str(a.first_date) if a.first_date else None,
                        "last_date": str(a.last_date) if a.last_date else None,
                        "count": a.count,
                    }
                    for a in alarms
                ]
            }
        except Exception:
            return {"active_alarms": []}


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the approved Vallox Extended binary sensors."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    async_add_entities(
        [
            ValloxExtendedBinarySensor(
                coordinator,
                "bypass_active",
                "Bypass active",
                "A_CYC_CELL_STATE",
                CELL_STATE_BYPASS,
                frozenset({0, 1, CELL_STATE_BYPASS, CELL_STATE_DEFROSTING}),
            ),
            ValloxExtendedBinarySensor(
                coordinator,
                "defrosting",
                "Defrosting",
                "A_CYC_CELL_STATE",
                CELL_STATE_DEFROSTING,
                frozenset({0, 1, CELL_STATE_BYPASS, CELL_STATE_DEFROSTING}),
            ),
            ValloxExtendedBinarySensor(
                coordinator,
                "post_heater",
                "Post-heater active",
                "A_CYC_IO_HEATER",
                1,
                frozenset({0, 1}),
            ),
            ValloxExtendedFaultActiveBinarySensor(coordinator),
        ]
    )
