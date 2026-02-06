"""DataUpdateCoordinator for MyLog."""
from __future__ import annotations

import logging
from datetime import timedelta
from typing import Any

from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import MyLogApi, MyLogApiError

_LOGGER = logging.getLogger(__name__)

UPDATE_INTERVAL = timedelta(minutes=5)


class MyLogCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Coordinator to fetch MyLog stats and recent entries."""

    def __init__(self, hass: HomeAssistant, api: MyLogApi) -> None:
        """Initialize the coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name="MyLog",
            update_interval=UPDATE_INTERVAL,
        )
        self.api = api

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from MyLog API."""
        try:
            stats = await self.api.get_stats()
            recent = await self.api.get_recent_entries(per_page=10)
            return {
                "stats": stats,
                "recent_entries": recent.get("data", []),
                "total_entries": recent.get("total", 0),
            }
        except MyLogApiError as err:
            raise UpdateFailed(f"Error fetching MyLog data: {err}") from err
