# ha-vallox-extended

Complete Vallox telemetry, diagnostics, and ventilation controls.

Home Assistant integration installed via HACS from
[timmikk/ha-vallox-extended](https://github.com/timmikk/ha-vallox-extended) (public
GitHub mirror of the Forgejo primary at
[git.clo.dy.fi/timo/ha-vallox-extended](https://git.clo.dy.fi/timo/ha-vallox-extended)).

## Features

- **Temperatures**: All 5 air stream temperatures (extract, exhaust, outdoor, supply, supply cell) plus optional duct temp with disconnected probe detection.
- **Heat Recovery**: Dual heat-recovery efficiencies (supply and extract).
- **Fan Telemetry & Control**: Fan speed percentage, supply/extract RPMs, fan balance base percentages, and motor output duty. Full fan control with presets (Home, Away, Boost, Fireplace, Extra).
- **Air Quality & Humidity**: Relative humidity, baseline RH, multisensor RH, plus capability-gated CO2 & VOC sensors.
- **Maintenance & Uptime**: Filter countdown (months), change interval (days), next filter change date, interactive last filter change date picker, current uptime, and lifetime machine uptime.
- **Modes & Diagnostics**: Cell state, supply heating adjust mode, defrost mode, defrost limit temp, post-heater winter setpoint, and rich active alarm diagnostics.
- **Controls**: Ventilation fan entity, profile supply air target temperatures, and bypass lock switch.

## Install

1. HACS → ⋮ → Custom repositories, add
   `https://github.com/timmikk/ha-vallox-extended`, category **Integration**.
2. HACS → Explore, find "Vallox Extended", Download.
3. Restart Home Assistant.
4. Settings → Devices & Services → Add Integration → Vallox Extended.

## Rollback

HACS → this integration → Redownload → pick prior version → restart HA.
