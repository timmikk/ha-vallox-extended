"""Tests for Vallox Extended switch platform."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_bypass_locked_switch(hass):
    """Test reading and toggling bypass locked switch."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics["A_CYC_BYPASS_LOCKED"] = 0

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

    state = hass.states.get("switch.vallox_extended_bypass_locked")
    assert state is not None
    assert state.state == "off"

    # Turn on
    await hass.services.async_call(
        "switch",
        "turn_on",
        {"entity_id": "switch.vallox_extended_bypass_locked"},
        blocking=True,
    )
    client.set_values.assert_awaited_with({"A_CYC_BYPASS_LOCKED": 1})

    # Turn off
    await hass.services.async_call(
        "switch",
        "turn_off",
        {"entity_id": "switch.vallox_extended_bypass_locked"},
        blocking=True,
    )
    client.set_values.assert_awaited_with({"A_CYC_BYPASS_LOCKED": 0})
