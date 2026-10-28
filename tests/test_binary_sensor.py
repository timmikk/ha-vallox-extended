"""Tests for Vallox Extended binary sensors."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_binary_sensors_and_alarm_attributes(hass):
    """Test bypass, defrost, post-heater, and rich fault active binary sensors."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_CELL_STATE": 2,  # Bypass active
            "A_CYC_IO_HEATER": 1,  # Post heater active
            "A_CYC_FAULT_ACTIVITY": 1,  # Fault active
            "A_CYC_TOTAL_FAULT_COUNT": 1,
            "A_CYC_FAULT_CODE": 12,
            "A_CYC_FAULT_SEVERITY": 1,
            "A_CYC_FAULT_COUNT": 2,
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

    state = hass.states.get("binary_sensor.vallox_extended_bypass_active")
    assert state is not None
    assert state.state == "on"

    state = hass.states.get("binary_sensor.vallox_extended_defrosting")
    assert state is not None
    assert state.state == "off"

    state = hass.states.get("binary_sensor.vallox_extended_post_heater_active")
    assert state is not None
    assert state.state == "on"

    state = hass.states.get("binary_sensor.vallox_extended_fault_active")
    assert state is not None
    assert state.state == "on"
    assert "active_alarms" in state.attributes
    alarms = state.attributes["active_alarms"]
    assert len(alarms) == 1
    assert alarms[0]["code"] == 12
    assert alarms[0]["count"] == 2
    assert alarms[0]["severity"] == "SEVERE"
    assert "freezing risk" in alarms[0]["message"].lower()
