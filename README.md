# ha-vallox-extended

Complete Vallox telemetry, diagnostics, and ventilation controls.

Home Assistant custom integration. Development happens on
[git.clo.dy.fi/timo/ha-vallox-extended](https://git.clo.dy.fi/timo/ha-vallox-extended);
the public GitHub mirror at
[timmikk/ha-vallox-extended](https://github.com/timmikk/ha-vallox-extended) is
HACS-installable. See `info.md` for install/rollback instructions.

## Development

- Component code lives in `custom_components/vallox_extended/`.
- Tests: `pytest` (uses `pytest-homeassistant-custom-component`).
- CI: `.forgejo/workflows/ci.yml` runs `hassfest` + `hacs/action` + pytest.
- Release: tag `vX.Y.Z` on Forgejo → mirror syncs → HACS offers the version
  in the UI. A GitHub Release object is not needed.

## Supported telemetry & controls

Version 0.2.0 exposes all validated telemetry and controls available on Vallox MV units:

### Telemetry & Diagnostics
- **Temperatures**: All 5 stream temperatures (extract, exhaust, outdoor, supply, supply cell) and optional duct temp sensor (automatically reports unavailable when disconnected at `<= -40 °C`).
- **Heat Recovery Efficiencies**: Dual measurement sensors for supply efficiency and extract efficiency.
- **Fan Telemetry & Motor Output**: Fan speed percentage, supply/extract fan speeds in RPM, fan balance base percentages, and motor control output duty.
- **Air Quality & Humidity**: Relative humidity, humidity basic level, multisensor RH, plus capability-gated CO2 & VOC sensors (guards against reporting 0 ppm or placeholder 1000 when hardware is not installed).
- **Maintenance & Machine Uptime**: Filter remaining months, filter change interval, calculated next filter change date, current uptime, and lifetime machine uptime.
- **Operating Modes & Heating**: Cell state (heat recovery, cool recovery, bypass, defrost), supply heating adjust mode, defrost mode, supply air defrost limit, and post-heater winter setpoint.
- **Alarms**: Active fault binary sensor with rich attribute representation (`active_alarms` listing code, severity, fault count, timestamps, and descriptive messages).

### Controls
- **Ventilation Fan**: Full fan entity supporting preset modes (Home, Away, Boost, Fireplace, Extra) and percentage speed control.
- **Profile Target Temperatures**: Number entities to configure target supply air temperatures for Home, Away, and Boost profiles (5.0 °C to 25.0 °C).
- **Filter Change Date**: Date entity to inspect and update the last filter change date.
- **Bypass Locked**: Switch entity to lock or unlock the heat-recovery bypass damper.

### Security & Protocol Boundary

The component accepts only an explicit allowlist of protocol metric keys in `ALLOWED_METRICS`. Credential-bearing registers (`A_CYC_MASTER_PASSWORD`, `A_CYC_PARENTAL_PASSWORD`, `A_CYC_USER_PASSWORD`) and raw device configurations are strictly rejected and never exposed or logged. All communication is 100% local websocket traffic between Home Assistant and the unit.

## Secrets policy

This repo is **public**. Never commit tokens, passwords, or personal data.
Home Assistant fills those at runtime from `configuration.yaml`, config-flow
options, or `secrets.yaml` on the host — none of that touches this repo.

## Pipeline

See [`docs/ha-custom-components.md`](https://git.clo.dy.fi/timo/infra/src/branch/main/docs/ha-custom-components.md)
in the infra repo for the full pipeline (Forgejo primary + public GitHub
mirror + HACS registration + release/rollback flow).
