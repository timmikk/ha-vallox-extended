"""Number platform for Vallox Extended."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import (
    NumberDeviceClass,
    NumberEntity,
    NumberEntityDescription,
    NumberMode,
)
from homeassistant.const import EntityCategory, UnitOfTemperature
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity


@dataclass(frozen=True, kw_only=True)
class ValloxExtendedNumberEntityDescription(NumberEntityDescription):
    """Describes a Vallox Extended number entity."""

    metric_key: str


NUMBER_ENTITIES: tuple[ValloxExtendedNumberEntityDescription, ...] = (
    ValloxExtendedNumberEntityDescription(
        key="supply_air_target_home",
        name="Supply air target home",
        metric_key="A_CYC_HOME_AIR_TEMP_TARGET",
        native_min_value=5.0,
        native_max_value=25.0,
        native_step=1.0,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.AUTO,
    ),
    ValloxExtendedNumberEntityDescription(
        key="supply_air_target_away",
        name="Supply air target away",
        metric_key="A_CYC_AWAY_AIR_TEMP_TARGET",
        native_min_value=5.0,
        native_max_value=25.0,
        native_step=1.0,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.AUTO,
    ),
    ValloxExtendedNumberEntityDescription(
        key="supply_air_target_boost",
        name="Supply air target boost",
        metric_key="A_CYC_BOOST_AIR_TEMP_TARGET",
        native_min_value=5.0,
        native_max_value=25.0,
        native_step=1.0,
        device_class=NumberDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        entity_category=EntityCategory.CONFIG,
        mode=NumberMode.AUTO,
    ),
)


class ValloxExtendedTargetTempNumber(ValloxExtendedEntity, NumberEntity):
    """Number entity for setting profile supply air target temperature."""

    entity_description: ValloxExtendedNumberEntityDescription

    def __init__(
        self,
        coordinator: ValloxExtendedCoordinator,
        description: ValloxExtendedNumberEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> float | None:
        val = self.coordinator.data.get(self.entity_description.metric_key)
        return float(val) if isinstance(val, (int, float)) else None

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.client.set_values(
            {self.entity_description.metric_key: float(value)}
        )
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vallox Extended number entities."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    async_add_entities(
        [
            ValloxExtendedTargetTempNumber(coordinator, description)
            for description in NUMBER_ENTITIES
        ]
    )
