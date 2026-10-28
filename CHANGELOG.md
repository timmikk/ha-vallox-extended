# Changelog

All notable changes to this project will be documented in this file. Format
follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/); this project
adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

## [0.2.0] - 2026-10-28

### Added

- Expanded protocol allowlist in `ALLOWED_METRICS` to support all verified Vallox device telemetry.
- Air stream temperatures for extract, exhaust, outdoor, supply, and supply cell air, plus optional duct temp sensor with disconnected probe detection (`<= -40 °C`).
- Dual heat-recovery measurement sensors for supply efficiency and extract efficiency.
- Fan speed percentage, supply and extract fan RPM measurement sensors, balance base percentages, and motor control output duty diagnostics.
- Environmental sensors for relative humidity, humidity basic level, and multisensor humidity.
- Capability-gated CO2 and VOC sensors that guard against reporting placeholder 0 ppm or 1000 when optional hardware is not fitted.
- Filter remaining time (months), filter change interval (days), and next filter change date sensors.
- Machine uptime tracking for current uptime and lifetime machine operating hours.
- Operating mode sensors for cell state, supply heating adjust mode, defrost mode, and temperature setpoints.
- Rich active alarm diagnostics on `fault_active` binary sensor with decoded codes, messages, severity, and count.
- Date platform entity `filter_change_date` to view and update the last filter change date.
- Switch platform entity `bypass_locked` to lock/unlock the bypass damper.
- Number platform entities `supply_air_target_home`, `supply_air_target_away`, and `supply_air_target_boost` for setting profile temperatures.
- Fan platform entity `fan.vallox_extended_ventilation_fan` with preset modes (Home, Away, Boost, Fireplace, Extra) and speed control.

## [0.1.2] - 2026-10-27

### Fixed

- Fixed `homeassistant` version format in `hacs.json` to CalVer without operator prefix (`2026.5.0`), resolving `AwesomeVersionCompareException` during HACS download.

## [0.1.1] - 2026-09-27

### Changed

- Renamed the repository and integration domain from `vallox_health` to
  `vallox_extended` before the first HACS installation.

## [0.1.0] - 2026-09-26

### Added

- Initial Vallox Extended integration with bypass, defrost, heater,
  and fault diagnostic telemetry.
- Explicit protocol allowlist and tests preventing unapproved raw fields from
  entering coordinator state.

## [0.0.1] - 2026-09-26

- Initial scaffold via infra task #200 (`scripts/setup-ha-component-repo.sh`).
  Empty `async_setup` shell; not yet functional.
