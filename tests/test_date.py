"""Tests for Vallox Extended date platform."""

from datetime import date
from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


@pytest.mark.asyncio
async def test_filter_change_date(hass):
    """Test reading and setting the filter change date."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_FILTER_CHANGED_YEAR": 26,
            "A_CYC_FILTER_CHANGED_MONTH": 5,
            "A_CYC_FILTER_CHANGED_DAY": 3,
        }
    )

    client = type(
        "Client",
        (),
        {
            "fetch_metrics": AsyncMock(return_value=mock_metrics),
            "set_filter_change_date": AsyncMock(),
        },
    )()
    entry = MockConfigEntry(domain=DOMAIN, data={CONF_HOST: "192.0.2.1"})
    entry.add_to_hass(hass)

    with patch("custom_components.vallox_extended.Vallox", return_value=client):
        assert await hass.config_entries.async_setup(entry.entry_id)
        await hass.async_block_till_done()

    state = hass.states.get("date.vallox_extended_filter_change_date")
    assert state is not None
    assert state.state == "2026-05-03"

    # Test setting date
    await hass.services.async_call(
        "date",
        "set_value",
        {"entity_id": "date.vallox_extended_filter_change_date", "date": "2026-06-01"},
        blocking=True,
    )
    client.set_filter_change_date.assert_awaited_once_with(date(2026, 6, 1))
