"""Tests for the Vallox Extended integration."""

from unittest.mock import AsyncMock, patch

import pytest
from homeassistant.config_entries import ConfigEntryState
from homeassistant.const import CONF_HOST
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.vallox_extended.const import ALLOWED_METRICS, DOMAIN


def test_import():
    """The integration package can be imported."""
    from custom_components import vallox_extended  # noqa: F401


def test_allowlist_contains_only_approved_metrics():
    """The component's protocol boundary stays explicit and excludes sensitive keys."""
    # Master and user passwords must never be in the allowlist
    assert "A_CYC_MASTER_PASSWORD" not in ALLOWED_METRICS
    assert "A_CYC_PARENTAL_PASSWORD" not in ALLOWED_METRICS
    assert "A_CYC_USER_PASSWORD" not in ALLOWED_METRICS

    # Core health and newly approved metrics are present
    assert "A_CYC_CELL_STATE" in ALLOWED_METRICS
    assert "A_CYC_IO_HEATER" in ALLOWED_METRICS
    assert "A_CYC_SUPPLY_EFFICIENCY" in ALLOWED_METRICS
    assert "A_CYC_EXTRACT_EFFICIENCY" in ALLOWED_METRICS
    assert "A_CYC_SUPP_FAN_SPEED" in ALLOWED_METRICS
    assert "A_CYC_EXTR_FAN_SPEED" in ALLOWED_METRICS
    assert "A_CYC_RH_VALUE" in ALLOWED_METRICS


@pytest.mark.asyncio
async def test_setup_and_unload_filters_unapproved_metrics(hass):
    """Setup creates the platforms while coordinator data stays allowlisted."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics["A_CYC_CELL_STATE"] = 2
    mock_metrics["UNAPPROVED_PROTOCOL_FIELD"] = 1
    mock_metrics["A_CYC_MASTER_PASSWORD"] = 1234

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

    assert entry.state is ConfigEntryState.LOADED
    coordinator = entry.runtime_data
    assert "UNAPPROVED_PROTOCOL_FIELD" not in coordinator.data
    assert "A_CYC_MASTER_PASSWORD" not in coordinator.data
    assert set(coordinator.data) == ALLOWED_METRICS

    assert await hass.config_entries.async_unload(entry.entry_id)
    await hass.async_block_till_done()
    assert entry.state is ConfigEntryState.NOT_LOADED
