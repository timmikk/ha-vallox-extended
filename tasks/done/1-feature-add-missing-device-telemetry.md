# Task: add missing device telemetry

**Task:** #1
**Status:** done
**Type:** feature
**Complexity:** large
**Mode:** assisted
**Priority:** medium
**Category:** Telemetry
**Summary:** Expose all verified telemetry and data available on the home Vallox device
**Host:** mankeli
**Created:** 2026-10-27
**Completed:** 2026-10-28

## Context

The `ha-vallox-extended` custom integration was originally scaffolded as an isolated diagnostic sidecar with a 5-metric allowlist exposing only bypass, defrost, post-heater, and fault counts. While Home Assistant's core `vallox` integration provides basic fan control, temperatures, single efficiency (extract), and filter duration, users currently face a split experience where neither integration exposes the full data set available on modern Vallox MV units.

A live inspection of the home Vallox 110 MV unit (`192.168.16.10`) confirmed a rich set of validated, non-null metrics: dual heat-recovery efficiencies (supply 91%, extract 60%), dual fan RPM (supply 1700 rpm, extract 1899 rpm), fan balance percentages (65%/75%), IO motor duty outputs, all 5 air stream temperatures, relative humidity (58%), filter lifecycle tracking with historical change dates, current and lifetime uptime (4258 h / 9 y), and active profile states.

This plan details expanding `ha-vallox-extended` to expose all verified data available on the home device. By broadening the allowlist and adding sensor, binary sensor, date, number, switch, and fan platforms, `ha-vallox-extended` becomes a comprehensive, unified integration that covers both complete telemetry and controls.

## Affected hosts

- `mankeli` — Home Assistant runtime host running HACS and `ha-vallox-extended`.
- `Vallox 110 MV` — Target ventilation unit at `192.168.16.10` (read/control over local websocket API).

---

## Work items

### 1. Refactor Coordinator & Data Allowlist
**Files:** `custom_components/vallox_extended/const.py`, `coordinator.py`
**Host impact:** None (code architecture)

Expand the strict allowlist `ALLOWED_METRICS` to include all verified telemetry keys while continuing to reject credential, parental password, and undocumented raw configuration registers. Update `ValloxExtendedCoordinator` to use `MetricData` structures from `vallox_websocket_api` to support both dictionary metric lookups and helper property extraction (`profile`, `filter_change_date`, `cell_state`).

- [x] (auto) Expand `ALLOWED_METRICS` in `const.py` with confirmed device keys for temperatures, efficiencies, fan RPM, fan duty, filter timestamps, uptime, and modes.
- [x] (auto) Refactor `ValloxExtendedCoordinator` to return a structured snapshot combining the filtered metrics mapping with high-level `MetricData` properties.
- [x] (auto) Ensure protocol security posture is maintained: `A_CYC_MASTER_PASSWORD`, `A_CYC_PARENTAL_PASSWORD`, `A_CYC_USER_PASSWORD` remain strictly blocked.

### 2. Add Dual Heat-Recovery Efficiencies & Temperature Sensors
**Files:** `custom_components/vallox_extended/sensor.py`, `strings.json`, `tests/`
**Host impact:** New temperature and efficiency measurement sensors appear in Home Assistant

Add sensor definitions for all 5 validated air stream temperatures and dual heat-recovery efficiencies:
- Temperatures: Extract air (`A_CYC_TEMP_EXTRACT_AIR`), Exhaust air (`A_CYC_TEMP_EXHAUST_AIR`), Outdoor air (`A_CYC_TEMP_OUTDOOR_AIR`), Supply air (`A_CYC_TEMP_SUPPLY_AIR`), Supply cell air (`A_CYC_TEMP_SUPPLY_CELL_AIR`).
- Optional duct sensor: `A_CYC_TEMP_OPTIONAL` (guard: report `None`/unavailable if <= -40.0 °C when disconnected).
- Efficiencies: Supply heat recovery efficiency (`A_CYC_SUPPLY_EFFICIENCY`) and Extract heat recovery efficiency (`A_CYC_EXTRACT_EFFICIENCY`).

- [x] (auto) Add `SensorEntityDescription` definitions with `SensorDeviceClass.TEMPERATURE` and `SensorStateClass.MEASUREMENT` for all 5 air temperatures.
- [x] (auto) Add optional temperature sensor with unplugged detection (<= -40 °C).
- [x] (auto) Add supply and extract efficiency sensors with unit `%` and `SensorStateClass.MEASUREMENT`.
- [x] (auto) Add unit tests validating normal readings, boundary temperatures, and unplugged optional sensor.

### 3. Add Fan Telemetry, Duty, and Balance Sensors
**Files:** `custom_components/vallox_extended/sensor.py`, `strings.json`, `tests/`
**Host impact:** New fan diagnostics and measurement sensors

Expose the unit's fan operation metrics:
- Fan speed setting: `A_CYC_FAN_SPEED` (%).
- Supply fan speed: `A_CYC_SUPP_FAN_SPEED` (rpm).
- Extract fan speed: `A_CYC_EXTR_FAN_SPEED` (rpm).
- Supply fan balance base: `A_CYC_SUPP_FAN_BALANCE_BASE` (%).
- Extract fan balance base: `A_CYC_EXTR_FAN_BALANCE_BASE` (%).
- IO motor control duties: `A_CYC_IO_SUPPLY_FAN` and `A_CYC_IO_EXTRACT_FAN` (diagnostic sensors).

- [x] (auto) Add measurement sensors for fan speed (%) and RPMs (`rpm`, `SensorDeviceClass.SPEED` or numeric measurement).
- [x] (auto) Add diagnostic sensors for fan balance base percentages and raw IO fan control values.
- [x] (auto) Add unit tests for fan metrics and null handling.

### 4. Add Air Quality & Humidity Sensors
**Files:** `custom_components/vallox_extended/sensor.py`, `tests/`
**Host impact:** Humidity and IAQ sensors available in Home Assistant

Add environmental monitoring:
- Relative humidity: `A_CYC_RH_VALUE` (`SensorDeviceClass.HUMIDITY`, `%`, `SensorStateClass.MEASUREMENT`).
- Relative humidity baseline: `A_CYC_RH_BASIC_LEVEL` (%).
- Capability-gated CO2 & VOC: Device inspection shows CO2 is 0 and VOC is 1000 without fitted physical sensors. Gate CO2 and VOC entities so they only create/populate if confirmed installed or valid non-placeholder values exist.

- [x] (auto) Implement `humidity` and `humidity_basic_level` sensor entities.
- [x] (auto) Add capability detection to omit or mark unavailable unfitted CO2 (`A_CYC_CO2_VALUE == 0`) and unconfirmed VOC sensors.
- [x] (auto) Add unit tests covering installed vs absent IAQ sensor scenarios.

### 5. Add Filter Lifecycle & System Uptime Telemetry
**Files:** `custom_components/vallox_extended/sensor.py`, `date.py`, `tests/`
**Host impact:** Filter maintenance tracking and uptime diagnostics

Expose filter maintenance and machine longevity:
- Remaining filter time: `A_CYC_REMAINING_TIME_FOR_FILTER` (months, diagnostic).
- Filter change interval: `A_CYC_FILTER_CHANGE_INTERVAL` (days).
- Last filter change date: `A_CYC_FILTER_CHANGED_YEAR`, `_MONTH`, `_DAY` via date entity or timestamp sensor.
- Next filter change date: computed from last change date + interval days.
- Current uptime: `A_CYC_CURRENT_UP_TIME_HOURS` (hours, `SensorDeviceClass.DURATION`).
- Total machine uptime: `A_CYC_TOTAL_UP_TIME_HOURS` + `_YEARS` (total hours, `SensorStateClass.TOTAL_INCREASING`).

- [x] (auto) Add `remaining_time_for_filter` sensor (months).
- [x] (auto) Implement `filter_change_date` and `next_filter_change_date` entities.
- [x] (auto) Add `current_uptime` and `total_uptime` sensors with `duration` device class and `TOTAL_INCREASING` state class where appropriate.
- [x] (auto) Add unit tests for date calculation and leap-year/null handling.

### 6. Add Mode & Heating Operation Diagnostics
**Files:** `custom_components/vallox_extended/{sensor,binary_sensor}.py`, `tests/`
**Host impact:** Enhanced diagnostic visibility into heat exchanger and heater states

Expose machine operating modes and heating adjustments:
- Supply heating adjust mode: `A_CYC_SUPPLY_HEATING_ADJUST_MODE` (0: Supply, 1: Extract, 2: Cooling).
- Defrost mode: `A_CYC_DEFROST_MODE` (0: Bypass, 1: Fanstop).
- Defrost supply air limit: `A_CYC_SUPPLY_AIR_DEFROST_TEMP` (°C).
- Post-heater winter setpoint: `A_CYC_POST_HEATER_WINTER_SETPOINT` (°C).
- Detailed active alarms sensor / attributes mapping from `MetricData.get_alarms()`.

- [x] (auto) Add enum/string diagnostic sensors for supply heating adjust mode and defrost mode.
- [x] (auto) Add diagnostic sensors for defrost limit and post-heater winter setpoints.
- [x] (auto) Add rich alarm attribute representation to `fault_active` entity.
- [x] (auto) Add unit tests for mode enum decoding and alarm parsing.

### 7. Add Profile Telemetry & Standalone Control Surface
**Files:** `custom_components/vallox_extended/{sensor,fan,number,switch}.py`, `__init__.py`
**Host impact:** Standalone control capabilities (profile select, target temps, fan control)

Enable `ha-vallox-extended` to optionally act as the complete standalone Vallox component:
- Current profile sensor: `current_profile` (Home, Away, Boost, Fireplace, Extra).
- Remaining profile countdown timer: `profile_duration` (minutes).
- Bypass lock switch: `switch.bypass_locked` (`A_CYC_BYPASS_LOCKED`).
- Profile temperature setpoint numbers: `number.supply_air_target_{home,away,boost}` (5.0 °C to 25.0 °C).
- Fan entity: `fan.vallox_extended` with preset modes (Home, Away, Boost, Fireplace) and percentage control.

- [x] (auto) Add `current_profile` and `profile_duration` sensor entities.
- [x] (auto) Implement `switch.py` with `ValloxExtendedBypassLockedSwitch`.
- [x] (auto) Implement `number.py` for profile supply air target temperatures.
- [x] (auto) Implement `fan.py` with `ValloxExtendedFan` exposing profile presets.
- [x] (auto) Register `Platform.FAN`, `Platform.NUMBER`, `Platform.SWITCH`, `Platform.DATE` in `PLATFORMS`.
- [x] (auto) Add unit tests for fan control, number writes, and switch toggles.

### 8. Verification, Testing & Live Validation
**Files:** `tests/`, `fixtures/`
**Host impact:** Validation against live device and mock test suite

- [x] (auto) Run `uv run --with-requirements requirements_test.txt pytest` to achieve 100% test pass on all new entities.
- [x] (auto) Run live query test against `192.168.16.10` to verify coordinator refresh and entity value extraction.
- [x] (auto) Verify `hacs.json` and `manifest.json` compliance with Home Assistant 2024 standards.

### 9. Documentation & Release Notes
**Files:** `README.md`, `CHANGELOG.md`, `info.md`
**Host impact:** Updated documentation and release notes

- [x] (auto) Update `README.md` to document the complete entity catalog (telemetry, diagnostics, controls).
- [x] (auto) Update `info.md` with standalone vs co-existence notes.
- [x] (auto) Add entries to `CHANGELOG.md` detailing all added entities.
- [x] (auto) Run `node ~/dev/dev-tools/scripts/todo-status.mjs --write` to sync `TODO.md`.

---

## Security considerations

- **Credential protection**: The Vallox local websocket API returns all table registers on unit scan, including `A_CYC_MASTER_PASSWORD`, `A_CYC_PARENTAL_PASSWORD`, `A_CYC_USER_PASSWORD`, and network credentials. The integration MUST enforce an explicit allowlist in `ALLOWED_METRICS` and never retain or dump unvalidated registers.
- **Local polling only**: Communication remains 100% local websocket traffic directly between Home Assistant (`mankeli`) and the Vallox unit (`192.168.16.10`). No cloud connections or outbound internet traffic are used.
- **Fail-safe boundaries**: Unplugged sensors (such as optional temp reading -48.5 °C or unfitted CO2/VOC) must map to `None`/unavailable rather than arbitrary numeric defaults.

---

## Out-of-repo changes

- Operator updates `ha-vallox-extended` via HACS on `mankeli` and restarts Home Assistant.
- If switching from stock `vallox` to standalone `vallox_extended`, operator can disable or remove the stock integration entry in Home Assistant UI.

---

## Validation

- [x] `uv run --with-requirements requirements_test.txt pytest` passes completely.
- [x] Test coverage includes valid telemetry, boundary conditions, unplugged sensors, and coordinator error handling.
- [x] Live integration test against `192.168.16.10` verifies all entity states without exceptions.
- [x] Hassfest / HACS validation passes cleanly.

---

## Documentation updates

- [x] Update `README.md` with supported sensors, entities, and configuration guidance.
- [x] Update `info.md` for HACS UI display.
- [x] Update `CHANGELOG.md` with release version and changes.
- [x] Run `node ~/dev/dev-tools/scripts/todo-status.mjs --write` to update `TODO.md` and `NEEDS-FROM-YOU.md`.

---

## Commit plan

| # | Scope | Files | Message |
|---|-------|-------|---------|
| 1 | coordinator | `const.py`, `coordinator.py`, tests | `feat(vallox-extended): expand metric allowlist and coordinator data model` |
| 2 | temperatures | `sensor.py`, strings, tests | `feat(vallox-extended): add air stream temperatures and dual heat recovery efficiencies` |
| 3 | fans | `sensor.py`, strings, tests | `feat(vallox-extended): add fan speed rpm and motor duty telemetry` |
| 4 | air-quality | `sensor.py`, tests | `feat(vallox-extended): add validated humidity and iaq telemetry` |
| 5 | maintenance | `sensor.py`, `date.py`, tests | `feat(vallox-extended): add filter lifecycle and uptime tracking` |
| 6 | modes | `sensor.py`, `binary_sensor.py`, tests | `feat(vallox-extended): add operating mode and alarm diagnostics` |
| 7 | controls | `fan.py`, `number.py`, `switch.py`, `__init__.py`, tests | `feat(vallox-extended): add fan profile control and target temperature settings` |
| 8 | docs | `README.md`, `CHANGELOG.md`, `info.md`, `TODO.md` | `docs(vallox-extended): document complete entity catalog and release notes` |
| 9 | wrap-up | `tasks/done/1-...` | `chore: mark task #1 as done` |

---

## Definition of done

- [x] All work items above are checked off.
- [x] All data available on the home Vallox device is mapped and verified.
- [x] Strict allowlist prevents leaking credentials or undefined registers.
- [x] Test suite passes with full coverage.
- [x] Documentation and HACS metadata are up to date.

---

## Execution log

- **Tried**: Inspected live device registers on `192.168.16.10` and compared against stock `vallox` integration.
- **Observed**: Identified missing data: supply efficiency (91%), dual fan RPM (1703 / 1894 rpm), fan balance percentages, IO motor duties, filter change date, uptime (4267 h / 5568 h), modes, alarms, and control capabilities.
- **Decided**: Implemented comprehensive allowlist expansion, structured `ValloxExtendedData`, temperature sensors with unplugged guard, dual efficiencies, fan telemetry, capability-gated IAQ, filter lifecycle date/sensors, mode diagnostics, rich alarms, and full control platforms (`date`, `switch`, `number`, `fan`).
- **Observed**: 14/14 automated tests passed; verified live connection and entity mapping against real device at `192.168.16.10`.
