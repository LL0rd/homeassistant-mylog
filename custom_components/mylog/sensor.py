"""MyLog sensors."""
from __future__ import annotations

import re
from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import MyLogCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up MyLog sensors."""
    coordinator: MyLogCoordinator = hass.data[DOMAIN][entry.entry_id]["coordinator"]

    sensors = [
        MyLogTotalEntriesSensor(coordinator, entry),
        MyLogMonthEntriesSensor(coordinator, entry),
        MyLogStorageSensor(coordinator, entry),
        MyLogRecentEntriesSensor(coordinator, entry),
    ]
    async_add_entities(sensors)


def _strip_html(text: str | None) -> str:
    """Strip HTML tags from text."""
    if not text:
        return ""
    return re.sub(r"<[^>]+>", "", text).strip()


class MyLogTotalEntriesSensor(CoordinatorEntity[MyLogCoordinator], SensorEntity):
    """Sensor for total log entries."""

    def __init__(self, coordinator: MyLogCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_total_entries"
        self._attr_name = "MyLog Total Entries"
        self._attr_icon = "mdi:notebook"

    @property
    def native_value(self) -> int:
        """Return total entries count."""
        if self.coordinator.data:
            return self.coordinator.data.get("stats", {}).get("total", 0)
        return 0


class MyLogMonthEntriesSensor(CoordinatorEntity[MyLogCoordinator], SensorEntity):
    """Sensor for entries this month."""

    def __init__(self, coordinator: MyLogCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_month_entries"
        self._attr_name = "MyLog Entries This Month"
        self._attr_icon = "mdi:calendar-month"

    @property
    def native_value(self) -> int:
        """Return monthly entries count."""
        if self.coordinator.data:
            return self.coordinator.data.get("stats", {}).get("thisMonth", 0)
        return 0


class MyLogStorageSensor(CoordinatorEntity[MyLogCoordinator], SensorEntity):
    """Sensor for storage used."""

    def __init__(self, coordinator: MyLogCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_storage_used"
        self._attr_name = "MyLog Storage Used"
        self._attr_icon = "mdi:harddisk"
        self._attr_native_unit_of_measurement = "MB"

    @property
    def native_value(self) -> float:
        """Return storage used in MB."""
        if self.coordinator.data:
            bytes_used = self.coordinator.data.get("stats", {}).get("storageUsed", 0)
            return round(bytes_used / (1024 * 1024), 1)
        return 0.0


class MyLogRecentEntriesSensor(CoordinatorEntity[MyLogCoordinator], SensorEntity):
    """Sensor showing the most recent log entries."""

    def __init__(self, coordinator: MyLogCoordinator, entry: ConfigEntry) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_recent_entries"
        self._attr_name = "MyLog Recent Entries"
        self._attr_icon = "mdi:format-list-bulleted"

    @property
    def native_value(self) -> int:
        """Return the number of recent entries available."""
        if self.coordinator.data:
            return len(self.coordinator.data.get("recent_entries", []))
        return 0

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return recent entries as attributes."""
        if not self.coordinator.data:
            return {"entries": []}

        raw_entries = self.coordinator.data.get("recent_entries", [])
        entries = []
        for entry in raw_entries:
            entries.append(
                {
                    "id": entry.get("id"),
                    "title": entry.get("title", ""),
                    "content": _strip_html(entry.get("content", "")),
                    "severity": entry.get("severity", "info"),
                    "tags": entry.get("tags", []),
                    "type": entry.get("typeName", ""),
                    "created_at": entry.get("createdAt", ""),
                    "occurred_at": entry.get("occurredAt", ""),
                }
            )

        return {"entries": entries}
