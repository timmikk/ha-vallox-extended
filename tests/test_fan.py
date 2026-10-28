"""Tests for Vallox Extended fan platform."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry
from vallox_websocket_api import Profile

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_fan_entity_presets_and_speed(hass):
    """Test reading and setting fan speed and presets."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_STATE": 0,  # Profile.HOME
            "A_CYC_MODE": 0,  # ON
            "A_CYC_FAN_SPEED": 60,
        }
    )

    client = type(
        "Client",
        (),
        {
            "fetch_metrics": AsyncMock(return_value=mock_metrics),
            "set_profile": AsyncMock(),
            "set_fan_speed": AsyncMock(),
            "set_values": AsyncMock(),
        },
    )()
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "192.0.2.1"})
    entry.add_to_hass(hass)

    with patch("custom_components.vallox_extended.Vallox", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("fan.vallox_extended_ventilation_fan")
    assert state is not None
    assert state.state == "on"
    assert state.attributes["preset_mode"] == "Home"
    assert state.attributes["percentage"] == 60

    # Set preset mode to Boost
    await hass.services.async_call(
        "fan",
        "set_preset_mode",
        {"entity_id": "fan.vallox_extended_ventilation_fan", "preset_mode": "Boost"},
        blocking=True,
    )
    client.set_profile.assert_awaited_with(Profile.BOOST)

    # Set fan speed percentage
    await hass.services.async_call(
        "fan",
        "set_percentage",
        {"entity_id": "fan.vallox_extended_ventilation_fan", "percentage": 75},
        blocking=True,
    )
    client.set_fan_speed.assert_awaited_with(Profile.HOME, 75)
