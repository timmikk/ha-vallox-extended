"""Constants for Vallox Extended.

The cell-state mapping is derived from Home Assistant's core Vallox
integration (Apache-2.0); only the read-only subset needed here is retained.
"""

from datetime import timedelta

DOMAIN = "vallox_extended"
DEFAULT_NAME = "Vallox Extended"
STATE_SCAN_INTERVAL = timedelta(seconds=60)

CELL_STATE_BYPASS = 2
CELL_STATE_DEFROSTING = 3

# Explicit telemetry allowlist. Raw Vallox responses include configuration
# and credential-bearing values (passwords, network tokens) and must never be exposed.
ALLOWED_METRICS = frozenset(
    {
        # Health, Cell state & Faults
        "A_CYC_CELL_STATE",
        "A_CYC_IO_HEATER",
        "A_CYC_FAULT_ACTIVITY",
        "A_CYC_FAULT_COUNT",
        "A_CYC_TOTAL_FAULT_COUNT",
        "A_CYC_FAULT_CODE",
        "A_CYC_FAULT_FIRST_DATE",
        "A_CYC_FAULT_LAST_DATE",
        "A_CYC_FAULT_SEVERITY",
        # Device info
        "A_CYC_MACHINE_MODEL",
        "A_CYC_MACHINE_TYPE",
        *(f"A_CYC_APPL_SW_VERSION_{i}" for i in range(1, 10)),
        *(f"A_CYC_UUID{i}" for i in range(8)),
        # Temperatures
        "A_CYC_TEMP_EXTRACT_AIR",
        "A_CYC_TEMP_EXHAUST_AIR",
        "A_CYC_TEMP_OUTDOOR_AIR",
        "A_CYC_TEMP_SUPPLY_AIR",
        "A_CYC_TEMP_SUPPLY_CELL_AIR",
        "A_CYC_TEMP_OPTIONAL",
        # Efficiencies
        "A_CYC_SUPPLY_EFFICIENCY",
        "A_CYC_EXTRACT_EFFICIENCY",
        # Fan telemetry & motor duty
        "A_CYC_FAN_SPEED",
        "A_CYC_SUPP_FAN_SPEED",
        "A_CYC_EXTR_FAN_SPEED",
        "A_CYC_SUPP_FAN_BALANCE_BASE",
        "A_CYC_EXTR_FAN_BALANCE_BASE",
        "A_CYC_IO_SUPPLY_FAN",
        "A_CYC_IO_EXTRACT_FAN",
        # Humidity & Air Quality
        "A_CYC_RH_VALUE",
        "A_CYC_RH_BASIC_LEVEL",
        "A_CYC_MULTISENSOR_RH",
        "A_CYC_CO2_VALUE",
        "A_CYC_VOC_LEVEL",
        # Filter & Uptime
        "A_CYC_REMAINING_TIME_FOR_FILTER",
        "A_CYC_FILTER_CHANGE_INTERVAL",
        "A_CYC_FILTER_CHANGED_YEAR",
        "A_CYC_FILTER_CHANGED_MONTH",
        "A_CYC_FILTER_CHANGED_DAY",
        "A_CYC_CURRENT_UP_TIME_HOURS",
        "A_CYC_TOTAL_UP_TIME_HOURS",
        "A_CYC_TOTAL_UP_TIME_YEARS",
        # Operating Modes & Heating
        "A_CYC_SUPPLY_HEATING_ADJUST_MODE",
        "A_CYC_DEFROST_MODE",
        "A_CYC_SUPPLY_AIR_DEFROST_TEMP",
        "A_CYC_POST_HEATER_WINTER_SETPOINT",
        # Profiles & Settings
        "A_CYC_STATE",
        "A_CYC_MODE",
        "A_CYC_BOOST_TIMER",
        "A_CYC_FIREPLACE_TIMER",
        "A_CYC_EXTRA_TIMER",
        "A_CYC_BYPASS_LOCKED",
        "A_CYC_HOME_AIR_TEMP_TARGET",
        "A_CYC_AWAY_AIR_TEMP_TARGET",
        "A_CYC_BOOST_AIR_TEMP_TARGET",
        "A_CYC_HOME_SPEED_SETTING",
        "A_CYC_AWAY_SPEED_SETTING",
        "A_CYC_BOOST_SPEED_SETTING",
        "A_CYC_FIREPLACE_SUPP_FAN",
        "A_CYC_FIREPLACE_EXTR_FAN",
        "A_CYC_BOOST_TIME",
        "A_CYC_FIREPLACE_TIME",
        "A_CYC_EXTRA_TIME",
    }
)
