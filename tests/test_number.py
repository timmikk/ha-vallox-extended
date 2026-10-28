"""Tests for Vallox Extended number platform."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_supply_air_target_temperatures(hass):
    """Test reading and setting profile supply air target temperatures."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_HOME_AIR_TEMP_TARGET": 15.0,
            "A_CYC_AWAY_AIR_TEMP_TARGET": 10.0,
            "A_CYC_BOOST_AIR_TEMP_TARGET": 18.0,
        }
    )

    client = type(
        "Client",
        (),
        {
            "fetch_metrics": AsyncMock(return_value=mock_metrics),
            "set_values": AsyncMock(),
        },
    )()
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "192.0.2.1"})
    entry.add_to_hass(hass)

    with patch("custom_components.vallox_extended.Vallox", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("number.vallox_extended_supply_air_target_home")
    assert state is not None
    assert state.state == "15.0"

    state = hass.states.get("number.vallox_extended_supply_air_target_away")
    assert state is not None
    assert state.state == "10.0"

    state = hass.states.get("number.vallox_extended_supply_air_target_boost")
    assert state is not None
    assert state.state == "18.0"

    # Set home target temperature to 17.0
    await hass.services.async_call(
        "number",
        "set_value",
        {"entity_id": "number.vallox_extended_supply_air_target_home", "value": 17.0},
        blocking=True,
    )
    client.set_values.assert_awaited_with({"A_CYC_HOME_AIR_TEMP_TARGET": 17.0})
