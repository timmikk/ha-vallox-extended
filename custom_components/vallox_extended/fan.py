"""Fan platform for Vallox Extended."""

from __future__ import annotations

from typing import Any

from homeassistant.components.fan import FanEntity, FanEntityFeature
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from vallox_websocket_api import Profile

from .coordinator import ValloxExtendedCoordinator
from .entity import ValloxExtendedEntity

MODE_ON = 0
MODE_OFF = 5

PRESET_MODE_TO_PROFILE = {
    "Home": Profile.HOME,
    "Away": Profile.AWAY,
    "Boost": Profile.BOOST,
    "Fireplace": Profile.FIREPLACE,
    "Extra": Profile.EXTRA,
}

PROFILE_TO_PRESET_MODE = {v: k for k, v in PRESET_MODE_TO_PROFILE.items()}


class ValloxExtendedFan(ValloxExtendedEntity, FanEntity):
    """Representation of the Vallox ventilation unit fan."""

    _attr_supported_features = (
        FanEntityFeature.PRESET_MODE
        | FanEntityFeature.SET_SPEED
        | FanEntityFeature.TURN_OFF
        | FanEntityFeature.TURN_ON
    )
    _enable_turn_on_off_backwards_compatibility = False
    _attr_preset_modes = list(PRESET_MODE_TO_PROFILE)

    def __init__(self, coordinator: ValloxExtendedCoordinator) -> None:
        super().__init__(coordinator, "fan")
        self._attr_name = "Ventilation fan"

    @property
    def is_on(self) -> bool:
        mode = self.coordinator.data.get("A_CYC_MODE")
        return mode != MODE_OFF

    @property
    def preset_mode(self) -> str | None:
        profile = self.coordinator.data.metric_data.profile
        return PROFILE_TO_PRESET_MODE.get(profile)

    @property
    def percentage(self) -> int | None:
        val = self.coordinator.data.get("A_CYC_FAN_SPEED")
        return int(val) if isinstance(val, (int, float)) else None

    async def async_set_preset_mode(self, preset_mode: str) -> None:
        if preset_mode in PRESET_MODE_TO_PROFILE:
            profile = PRESET_MODE_TO_PROFILE[preset_mode]
            await self.coordinator.client.set_profile(profile)
            await self.coordinator.async_request_refresh()

    async def async_set_percentage(self, percentage: int) -> None:
        if percentage == 0:
            await self.async_turn_off()
            return

        profile = self.coordinator.data.metric_data.profile
        # If currently in a profile that doesn't support fan speed adjustment, default to HOME
        try:
            await self.coordinator.client.set_fan_speed(profile, percentage)
        except Exception:
            await self.coordinator.client.set_fan_speed(Profile.HOME, percentage)
        await self.coordinator.async_request_refresh()

    async def async_turn_on(
        self,
        percentage: int | None = None,
        preset_mode: str | None = None,
        **kwargs: Any,
    ) -> None:
        await self.coordinator.client.set_values({"A_CYC_MODE": MODE_ON})
        if preset_mode:
            await self.async_set_preset_mode(preset_mode)
        elif percentage is not None:
            await self.async_set_percentage(percentage)
        await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.client.set_values({"A_CYC_MODE": MODE_OFF})
        await self.coordinator.async_request_refresh()


async def async_setup_entry(
    _hass, entry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up the Vallox Extended fan entity."""
    coordinator: ValloxExtendedCoordinator = entry.runtime_data
    async_add_entities([ValloxExtendedFan(coordinator)])
