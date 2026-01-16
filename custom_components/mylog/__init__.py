"""MyLog Integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_API_KEY
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .api import MyLogApi, MyLogConnectionError, MyLogApiError
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

SERVICE_SEND_LOG = "send_log"
SERVICE_SEND_BATCH = "send_batch"

SERVICE_SEND_LOG_SCHEMA = vol.Schema(
    {
        vol.Optional("title"): cv.string,
        vol.Optional("content"): cv.string,
        vol.Optional("type_name"): cv.string,
        vol.Optional("type_id"): cv.positive_int,
        vol.Optional("severity"): vol.In(["info", "low", "medium", "high", "critical"]),
        vol.Optional("priority"): vol.All(vol.Coerce(int), vol.Range(min=0, max=100)),
        vol.Optional("status"): vol.In(["draft", "active", "archived"]),
        vol.Optional("tags"): vol.All(cv.ensure_list, [cv.string]),
        vol.Optional("location_name"): cv.string,
        vol.Optional("location_lat"): vol.All(
            vol.Coerce(float), vol.Range(min=-90, max=90)
        ),
        vol.Optional("location_lng"): vol.All(
            vol.Coerce(float), vol.Range(min=-180, max=180)
        ),
        vol.Optional("occurred_at"): cv.string,
        vol.Optional("is_favourite"): cv.boolean,
        vol.Optional("is_starred"): cv.boolean,
        vol.Optional("is_pinned"): cv.boolean,
        vol.Optional("is_public"): cv.boolean,
        vol.Optional("external_ref_id"): cv.string,
    }
)

SERVICE_SEND_BATCH_SCHEMA = vol.Schema(
    {
        vol.Required("entries"): vol.All(cv.ensure_list, [SERVICE_SEND_LOG_SCHEMA]),
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up MyLog from a config entry."""
    api = MyLogApi(entry.data[CONF_API_KEY])

    try:
        await api.health_check()
    except MyLogConnectionError as err:
        await api.close()
        raise ConfigEntryNotReady(f"Cannot connect to MyLog: {err}") from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = api

    async def handle_send_log(call: ServiceCall) -> None:
        """Handle send_log service call."""
        try:
            result = await api.create_log_entry(
                title=call.data.get("title"),
                content=call.data.get("content"),
                type_name=call.data.get("type_name"),
                type_id=call.data.get("type_id"),
                severity=call.data.get("severity", "info"),
                priority=call.data.get("priority", 0),
                status=call.data.get("status"),
                tags=call.data.get("tags"),
                location_name=call.data.get("location_name"),
                location_lat=call.data.get("location_lat"),
                location_lng=call.data.get("location_lng"),
                occurred_at=call.data.get("occurred_at"),
                is_favourite=call.data.get("is_favourite"),
                is_starred=call.data.get("is_starred"),
                is_pinned=call.data.get("is_pinned"),
                is_public=call.data.get("is_public"),
                external_ref_id=call.data.get("external_ref_id"),
            )
            _LOGGER.debug("Log entry created: %s", result)
        except MyLogApiError as err:
            _LOGGER.error("Failed to create log entry: %s", err)
            raise

    async def handle_send_batch(call: ServiceCall) -> None:
        """Handle send_batch service call."""
        entries = call.data.get("entries", [])
        try:
            result = await api.create_batch_entries(entries)
            _LOGGER.debug(
                "Batch created: %d succeeded, %d failed",
                result.get("created", 0),
                result.get("failed", 0),
            )
        except MyLogApiError as err:
            _LOGGER.error("Failed to create batch entries: %s", err)
            raise

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_LOG, handle_send_log, schema=SERVICE_SEND_LOG_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_BATCH, handle_send_batch, schema=SERVICE_SEND_BATCH_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    api: MyLogApi = hass.data[DOMAIN].pop(entry.entry_id)
    await api.close()

    # Remove services if no more entries
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_SEND_LOG)
        hass.services.async_remove(DOMAIN, SERVICE_SEND_BATCH)

    return True
