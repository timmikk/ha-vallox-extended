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
    assert state.state in ("unknown", "unavailable")

    # Efficiencies
    state = hass.states.get("sensor.vallox_extended_supply_heat_recovery_efficiency")
    assert state is not None
    assert state.state == "91"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_extract_heat_recovery_efficiency")
    assert state is not None
    assert state.state == "60"
    assert state.attributes["unit_of_measurement"] == "%"


@pytest.mark.asyncio
async def test_fan_telemetry_and_duty(hass):
    """Test fan speeds, RPMs, balance base, and IO motor duties."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_FAN_SPEED": 60,
            "A_CYC_SUPP_FAN_SPEED": 1700,
            "A_CYC_EXTR_FAN_SPEED": 1899,
            "A_CYC_SUPP_FAN_BALANCE_BASE": 65,
            "A_CYC_EXTR_FAN_BALANCE_BASE": 75,
            "A_CYC_IO_SUPPLY_FAN": 150,
            "A_CYC_IO_EXTRACT_FAN": 169,
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

    state = hass.states.get("sensor.vallox_extended_fan_speed")
    assert state is not None
    assert state.state == "60"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_supply_fan_speed")
    assert state is not None
    assert state.state == "1700"
    assert state.attributes["unit_of_measurement"] == "rpm"

    state = hass.states.get("sensor.vallox_extended_extract_fan_speed")
    assert state is not None
    assert state.state == "1899"
    assert state.attributes["unit_of_measurement"] == "rpm"

    state = hass.states.get("sensor.vallox_extended_supply_fan_balance_base")
    assert state is not None
    assert state.state == "65"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_extract_fan_balance_base")
    assert state is not None
    assert state.state == "75"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_supply_fan_control_output")
    assert state is not None
    assert state.state == "150"

    state = hass.states.get("sensor.vallox_extended_extract_fan_control_output")
    assert state is not None
    assert state.state == "169"


@pytest.mark.asyncio
async def test_iaq_and_humidity(hass):
    """Test humidity sensors and capability-gated CO2 and VOC sensors."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_RH_VALUE": 58,
            "A_CYC_RH_BASIC_LEVEL": 59,
            "A_CYC_MULTISENSOR_RH": 58,
            "A_CYC_CO2_VALUE": 0,  # Unfitted sensor returns 0
            "A_CYC_VOC_LEVEL": 1000,  # Unfitted sensor returns 1000
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

    # Humidity
    state = hass.states.get("sensor.vallox_extended_humidity")
    assert state is not None
    assert state.state == "58"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_humidity_basic_level")
    assert state is not None
    assert state.state == "59"
    assert state.attributes["unit_of_measurement"] == "%"

    state = hass.states.get("sensor.vallox_extended_multisensor_humidity")
    assert state is not None
    assert state.state == "58"
    assert state.attributes["unit_of_measurement"] == "%"

    # Unfitted CO2 and VOC sensors must report unavailable/unknown rather than 0 ppm or 1000
    state = hass.states.get("sensor.vallox_extended_carbon_dioxide")
    assert state is not None
    assert state.state in ("unknown", "unavailable")

    state = hass.states.get("sensor.vallox_extended_voc_level")
    assert state is not None
    assert state.state in ("unknown", "unavailable")


@pytest.mark.asyncio
async def test_iaq_fitted_sensors(hass):
    """Test CO2 and VOC when valid non-placeholder values are reported."""
    mock_metrics = {key: 0 for key in ALLOWED_METRICS}
    mock_metrics.update(
        {
            "A_CYC_CO2_VALUE": 650,
            "A_CYC_VOC_LEVEL": 150,
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

    state = hass.states.get("sensor.vallox_extended_carbon_dioxide")
    assert state is not None
    assert state.state == "650"
    assert state.attributes["unit_of_measurement"] == "ppm"

    state = hass.states.get("sensor.vallox_extended_voc_level")
    assert state is not None
    assert state.state == "150"
