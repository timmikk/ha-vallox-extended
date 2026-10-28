"""Read-only Vallox Extended numeric and telemetry sensors."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfTemperature,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity


@dataclass(frozen=True, kw_only=True)
class ValloxExtendedSensorEntityDescription(SensorEntityDescription):
    """Describes a Vallox Extended sensor."""

    metric_key: str | None = None


class ValloxExtendedSensor(ValloxExtendedEntity, SensorEntity):
    """Base sensor for Vallox Extended."""

    entity_description: ValloxExtendedSensorEntityDescription

    def __init__(
        self,
        coordinator: ValloxExtendedCoordinator,
        description: ValloxExtendedSensorEntityDescription,
    ) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def native_value(self) -> Any:
        if self.entity_description.metric_key:
            return self.coordinator.data.get(self.entity_description.metric_key)
        return None


class ValloxExtendedOptionalAirSensor(ValloxExtendedSensor):
    """Sensor for optional air temperature which guards against disconnected probes."""

    @property
    def native_value(self) -> float | None:
        val = super().native_value
        if val is None or (isinstance(val, (int, float)) and val <= -40.0):
            return None
        return val


class ValloxExtendedFaultCountSensor(ValloxExtendedSensor):
    """Expose a read-only Vallox fault counter."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC
    _attr_native_unit_of_measurement = "faults"


TEMPERATURE_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="extract_air",
        name="Extract air",
        metric_key="A_CYC_TEMP_EXTRACT_AIR",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="exhaust_air",
        name="Exhaust air",
        metric_key="A_CYC_TEMP_EXHAUST_AIR",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="outdoor_air",
        name="Outdoor air",
        metric_key="A_CYC_TEMP_OUTDOOR_AIR",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="supply_air",
        name="Supply air",
        metric_key="A_CYC_TEMP_SUPPLY_AIR",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="supply_cell_air",
        name="Supply cell air",
        metric_key="A_CYC_TEMP_SUPPLY_CELL_AIR",
        device_class=SensorDeviceClass.TEMPERATURE,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
)

EFFICIENCY_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="supply_efficiency",
        name="Supply heat recovery efficiency",
        metric_key="A_CYC_SUPPLY_EFFICIENCY",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="extract_efficiency",
        name="Extract heat recovery efficiency",
        metric_key="A_CYC_EXTRACT_EFFICIENCY",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
)

FAN_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="fan_speed",
        name="Fan speed",
        metric_key="A_CYC_FAN_SPEED",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="supply_fan_speed",
        name="Supply fan speed",
        metric_key="A_CYC_SUPP_FAN_SPEED",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="extract_fan_speed",
        name="Extract fan speed",
        metric_key="A_CYC_EXTR_FAN_SPEED",
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=REVOLUTIONS_PER_MINUTE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="supply_fan_balance_base",
        name="Supply fan balance base",
        metric_key="A_CYC_SUPP_FAN_BALANCE_BASE",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="extract_fan_balance_base",
        name="Extract fan balance base",
        metric_key="A_CYC_EXTR_FAN_BALANCE_BASE",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="io_supply_fan",
        name="Supply fan control output",
        metric_key="A_CYC_IO_SUPPLY_FAN",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    ValloxExtendedSensorEntityDescription(
        key="io_extract_fan",
        name="Extract fan control output",
        metric_key="A_CYC_IO_EXTRACT_FAN",
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
)


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the approved Vallox Extended sensors."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    entities: list[SensorEntity] = [
        ValloxExtendedSensor(coordinator, desc) for desc in TEMPERATURE_SENSORS
    ]
    entities.append(
        ValloxExtendedOptionalAirSensor(
            coordinator,
            ValloxExtendedSensorEntityDescription(
                key="optional_air",
                name="Optional air",
                metric_key="A_CYC_TEMP_OPTIONAL",
                device_class=SensorDeviceClass.TEMPERATURE,
                state_class=SensorStateClass.MEASUREMENT,
                native_unit_of_measurement=UnitOfTemperature.CELSIUS,
            ),
        )
    )
    entities.extend(
        ValloxExtendedSensor(coordinator, desc) for desc in EFFICIENCY_SENSORS
    )
    entities.extend(
        ValloxExtendedSensor(coordinator, desc) for desc in FAN_SENSORS
    )
    entities.extend(
        [
            ValloxExtendedFaultCountSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="current_fault_count",
                    name="Current fault count",
                    metric_key="A_CYC_FAULT_COUNT",
                ),
            ),
            ValloxExtendedFaultCountSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="total_fault_count",
                    name="Total fault count",
                    metric_key="A_CYC_TOTAL_FAULT_COUNT",
                    state_class=SensorStateClass.TOTAL_INCREASING,
                ),
            ),
        ]
    )
    async_add_entities(entities)
