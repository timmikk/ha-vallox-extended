"""Tests for Vallox Extended sensor platform."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_temperatures_and_efficiencies(hass):
    """Test temperatures, disconnected optional temp guard, and efficiencies."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_TEMP_EXTRACT_AIR": 20.0,
            "A_CYC_TEMP_EXHAUST_AIR": 19.2,
            "A_CYC_TEMP_OUTDOOR_AIR": 9.8,
            "A_CYC_TEMP_SUPPLY_AIR": 12.4,
            "A_CYC_TEMP_SUPPLY_CELL_AIR": 11.7,
            "A_CYC_TEMP_OPTIONAL": -48.5,  # Unplugged probe
            "A_CYC_SUPPLY_EFFICIENCY": 91,
            "A_CYC_EXTRACT_EFFICIENCY": 60,
            "A_CYC_FAULT_COUNT": 0,
            "A_CYC_TOTAL_FAULT_COUNT": 0,
        }
    )

    client = type(
        "Client",
        (),
        {
            "fetch_metrics": AsyncMock(return_value=mock_metrics),
        },
    )()
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "192.0.2.1"})
    entry.add_to_hass(hass)

    with patch("custom_components.vallox_extended.Vallox", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    # Temperature states
    state = hass.states.get("sensor.vallox_extended_extract_air")
    assert state is not None
    assert state.state == "20.0"
    assert state.attributes["unit_of_measurement"] == "°C"

    state = hass.states.get("sensor.vallox_extended_outdoor_air")
    assert state is not None
    assert state.state == "9.8"

    # Optional temp sensor is unplugged (-48.5 °C), so it should report unavailable / None
    state = hass.states.get("sensor.vallox_extended_optional_air")
    assert state is not None
    assert state.state == "unknown" or state.state == "unavailable"

    # Efficiencies
    state = hass.states.get("sensor.vallox_extended_supply_heat_recovery_efficiency")
    assert state is not None
    assert state.state == "91"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_extract_heat_recovery_efficiency")
    assert state is not None
    assert state.state == "60"
    assert state.attributes["unit_of_measurement"] == "%"
