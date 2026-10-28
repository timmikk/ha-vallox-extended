"""Read-only polling coordinator for Vallox Extended."""

from __future__ import annotations

import logging
from collections.abc import Iterator, Mapping
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from vallox_websocket_api import MetricData, Vallox, ValloxApiException

from .const import ALLOWED_METRICS, DOMAIN, STATE_SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)


class ValloxExtendedData(Mapping[str, Any]):
    """Container holding allowlisted metrics and high-level MetricData helpers."""

    def __init__(self, metrics: Mapping[str, Any]) -> None:
        self._metrics = dict(metrics)
        self._metric_data = MetricData(self._metrics)

    def __getitem__(self, key: str) -> Any:
        return self._metrics[key]

    def __iter__(self) -> Iterator[str]:
        return iter(self._metrics)

    def __len__(self) -> int:
        return len(self._metrics)

    def get(self, key: str, default: Any = None) -> Any:
        return self._metrics.get(key, default)

    @property
    def metric_data(self) -> MetricData:
        """Return the underlying vallox_websocket_api MetricData helper."""
        return self._metric_data


class ValloxExtendedCoordinator(DataUpdateCoordinator[ValloxExtendedData]):
    """Fetch and retain only the explicitly approved Vallox metrics."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry, client: Vallox) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} data coordinator",
            update_interval=STATE_SCAN_INTERVAL,
        )
        self.client = client

    async def _async_update_data(self) -> ValloxExtendedData:
        try:
            data = await self.client.fetch_metrics()
        except ValloxApiException as err:
            raise UpdateFailed("Unable to refresh Vallox Extended metrics") from err
        filtered = {key: data.get(key) for key in ALLOWED_METRICS}
        return ValloxExtendedData(filtered)
