"""Read-only Vallox Extended numeric and telemetry sensors."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    CONCENTRATION_PARTS_PER_MILLION,
    PERCENTAGE,
    REVOLUTIONS_PER_MINUTE,
    EntityCategory,
    UnitOfTemperature,
    UnitOfTime,
)
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vallox_websocket_api import Profile

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


class ValloxExtendedCO2Sensor(ValloxExtendedSensor):
    """CO2 sensor that guards against 0 ppm placeholder when no sensor is fitted."""

    @property
    def native_value(self) -> int | None:
        val = super().native_value
        if val is None or val == 0:
            return None
        return val


class ValloxExtendedVOCSensor(ValloxExtendedSensor):
    """VOC sensor that guards against 1000 placeholder when no sensor is fitted."""

    @property
    def native_value(self) -> int | None:
        val = super().native_value
        if val is None or val == 1000:
            return None
        return val


class ValloxExtendedNextFilterChangeDateSensor(ValloxExtendedSensor):
    """Sensor exposing next filter change date."""

    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> date | None:
        try:
            return self.coordinator.data.metric_data.next_filter_change_date
        except (ValueError, TypeError):
            return None


VALLOX_CELL_STATE_MAP = {
    0: "heat_recovery",
    1: "cool_recovery",
    2: "bypass",
    3: "defrost",
}

VALLOX_SUPPLY_HEATING_ADJUST_MODE_MAP = {
    0: "supply",
    1: "extract",
    2: "cooling",
}

VALLOX_DEFROST_MODE_MAP = {
    0: "bypass",
    1: "fanstop",
}

PROFILE_TO_PRESET_MODE = {
    Profile.HOME: "Home",
    Profile.AWAY: "Away",
    Profile.BOOST: "Boost",
    Profile.FIREPLACE: "Fireplace",
    Profile.EXTRA: "Extra",
}


class ValloxExtendedCellStateSensor(ValloxExtendedSensor):
    """Sensor exposing current cell state."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["heat_recovery", "cool_recovery", "bypass", "defrost"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        val = super().native_value
        return VALLOX_CELL_STATE_MAP.get(val)


class ValloxExtendedSupplyHeatingAdjustModeSensor(ValloxExtendedSensor):
    """Sensor exposing supply heating adjust mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["supply", "extract", "cooling"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        val = super().native_value
        return VALLOX_SUPPLY_HEATING_ADJUST_MODE_MAP.get(val)


class ValloxExtendedDefrostModeSensor(ValloxExtendedSensor):
    """Sensor exposing defrost mode."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["bypass", "fanstop"]
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> str | None:
        val = super().native_value
        return VALLOX_DEFROST_MODE_MAP.get(val)


class ValloxExtendedProfileSensor(ValloxExtendedSensor):
    """Sensor exposing active profile."""

    _attr_device_class = SensorDeviceClass.ENUM
    _attr_options = ["Home", "Away", "Boost", "Fireplace", "Extra"]

    @property
    def native_value(self) -> str | None:
        try:
            profile = self.coordinator.data.metric_data.profile
            return PROFILE_TO_PRESET_MODE.get(profile)
        except Exception:
            return None


class ValloxExtendedProfileDurationSensor(ValloxExtendedSensor):
    """Sensor exposing remaining profile duration in minutes."""

    _attr_device_class = SensorDeviceClass.DURATION
    _attr_state_class = SensorStateClass.MEASUREMENT
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    @property
    def native_value(self) -> int | None:
        try:
            profile = self.coordinator.data.metric_data.profile
            return self.coordinator.data.metric_data.get_remaining_profile_duration(profile)
        except Exception:
            return None


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

IAQ_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="humidity",
        name="Humidity",
        metric_key="A_CYC_RH_VALUE",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="humidity_basic_level",
        name="Humidity basic level",
        metric_key="A_CYC_RH_BASIC_LEVEL",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=PERCENTAGE,
    ),
    ValloxExtendedSensorEntityDescription(
        key="multisensor_humidity",
        name="Multisensor humidity",
        metric_key="A_CYC_MULTISENSOR_RH",
        device_class=SensorDeviceClass.HUMIDITY,
        state_class=SensorStateClass.MEASUREMENT,
        native_unit_of_measurement=PERCENTAGE,
    ),
)

MAINTENANCE_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="remaining_time_for_filter",
        name="Remaining time for filter",
        metric_key="A_CYC_REMAINING_TIME_FOR_FILTER",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="months",
    ),
    ValloxExtendedSensorEntityDescription(
        key="filter_change_interval",
        name="Filter change interval",
        metric_key="A_CYC_FILTER_CHANGE_INTERVAL",
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement="days",
    ),
    ValloxExtendedSensorEntityDescription(
        key="current_uptime",
        name="Current uptime",
        metric_key="A_CYC_CURRENT_UP_TIME_HOURS",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.HOURS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="total_uptime",
        name="Total uptime",
        metric_key="A_CYC_TOTAL_UP_TIME_HOURS",
        device_class=SensorDeviceClass.DURATION,
        state_class=SensorStateClass.TOTAL_INCREASING,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTime.HOURS,
    ),
)

MODE_DIAGNOSTIC_SENSORS: tuple[ValloxExtendedSensorEntityDescription, ...] = (
    ValloxExtendedSensorEntityDescription(
        key="supply_air_defrost_temp",
        name="Supply air defrost limit",
        metric_key="A_CYC_SUPPLY_AIR_DEFROST_TEMP",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
    ),
    ValloxExtendedSensorEntityDescription(
        key="post_heater_winter_setpoint",
        name="Post-heater winter setpoint",
        metric_key="A_CYC_POST_HEATER_WINTER_SETPOINT",
        device_class=SensorDeviceClass.TEMPERATURE,
        entity_category=EntityCategory.DIAGNOSTIC,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
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
        ValloxExtendedSensor(coordinator, desc) for desc in IAQ_SENSORS
    )
    entities.extend(
        ValloxExtendedSensor(coordinator, desc) for desc in MAINTENANCE_SENSORS
    )
    entities.extend(
        ValloxExtendedSensor(coordinator, desc) for desc in MODE_DIAGNOSTIC_SENSORS
    )
    entities.extend(
        [
            ValloxExtendedProfileSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="current_profile",
                    name="Current profile",
                ),
            ),
            ValloxExtendedProfileDurationSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="profile_duration",
                    name="Profile duration",
                ),
            ),
            ValloxExtendedCellStateSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="cell_state",
                    name="Cell state",
                    metric_key="A_CYC_CELL_STATE",
                ),
            ),
            ValloxExtendedSupplyHeatingAdjustModeSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="supply_heating_adjust_mode",
                    name="Supply heating adjust mode",
                    metric_key="A_CYC_SUPPLY_HEATING_ADJUST_MODE",
                ),
            ),
            ValloxExtendedDefrostModeSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="defrost_mode",
                    name="Defrost mode",
                    metric_key="A_CYC_DEFROST_MODE",
                ),
            ),
            ValloxExtendedNextFilterChangeDateSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="next_filter_change_date",
                    name="Next filter change date",
                    device_class=SensorDeviceClass.DATE,
                ),
            ),
            ValloxExtendedCO2Sensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="co2",
                    name="Carbon dioxide",
                    metric_key="A_CYC_CO2_VALUE",
                    device_class=SensorDeviceClass.CO2,
                    state_class=SensorStateClass.MEASUREMENT,
                    native_unit_of_measurement=CONCENTRATION_PARTS_PER_MILLION,
                ),
            ),
            ValloxExtendedVOCSensor(
                coordinator,
                ValloxExtendedSensorEntityDescription(
                    key="voc_level",
                    name="VOC level",
                    metric_key="A_CYC_VOC_LEVEL",
                    entity_category=EntityCategory.DIAGNOSTIC,
                ),
            ),
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
