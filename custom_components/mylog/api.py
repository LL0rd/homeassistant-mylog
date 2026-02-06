"""MyLog API Client."""
from __future__ import annotations

import aiohttp
from typing import Any

# Fixed API URLs - mylog.zip is the only instance
RUST_API_URL = "https://mylog.zip/fastAPI"
NUXT_API_URL = "https://mylog.zip/api"


class MyLogApiError(Exception):
    """Base exception for MyLog API errors."""

    pass


class MyLogAuthError(MyLogApiError):
    """Authentication error."""

    pass


class MyLogConnectionError(MyLogApiError):
    """Connection error."""

    pass


class MyLogApi:
    """Async client for MyLog API."""

    def __init__(self, api_key: str, session: aiohttp.ClientSession) -> None:
        """Initialize the API client."""
        self._rust_api_url = RUST_API_URL
        self._nuxt_api_url = NUXT_API_URL
        self._api_key = api_key
        self._session = session

    @property
    def _headers(self) -> dict[str, str]:
        """Return headers for API requests."""
        return {
            "Content-Type": "application/json",
            "X-API-Key": self._api_key,
        }

    async def health_check(self) -> dict[str, Any]:
        """Check API health."""
        session = self._session
        try:
            async with session.get(
                f"{self._rust_api_url}/health",
                timeout=aiohttp.ClientTimeout(total=10),
            ) as response:
                if response.status != 200:
                    raise MyLogConnectionError(
                        f"Health check failed: {response.status}"
                    )
                return await response.json()
        except aiohttp.ClientError as err:
            raise MyLogConnectionError(f"Connection failed: {err}") from err

    async def create_log_entry(
        self,
        title: str | None = None,
        content: str | None = None,
        type_name: str | None = None,
        type_id: int | None = None,
        severity: str = "info",
        priority: int = 0,
        status: str | None = None,
        tags: list[str] | None = None,
        location_name: str | None = None,
        location_lat: float | None = None,
        location_lng: float | None = None,
        occurred_at: str | None = None,
        is_favourite: bool | None = None,
        is_starred: bool | None = None,
        is_pinned: bool | None = None,
        is_public: bool | None = None,
        external_ref_id: str | None = None,
    ) -> dict[str, Any]:
        """Create a log entry."""
        payload = {
            k: v
            for k, v in {
                "title": title,
                "content": content,
                "type_name": type_name,
                "type_id": type_id,
                "severity": severity,
                "priority": priority,
                "status": status,
                "tags": tags,
                "location_name": location_name,
                "location_lat": location_lat,
                "location_lng": location_lng,
                "occurred_at": occurred_at,
                "is_favourite": is_favourite,
                "is_starred": is_starred,
                "is_pinned": is_pinned,
                "is_public": is_public,
                "external_ref_id": external_ref_id,
            }.items()
            if v is not None
        }

        session = self._session
        try:
            async with session.post(
                f"{self._rust_api_url}/api/v1/logs",
                json=payload,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=30),
            ) as response:
                data = await response.json()

                if response.status == 401:
                    raise MyLogAuthError(data.get("error", "Authentication failed"))
                if response.status >= 400:
                    raise MyLogApiError(
                        data.get("error", f"API error: {response.status}")
                    )

                return data
        except aiohttp.ClientError as err:
            raise MyLogConnectionError(f"Connection failed: {err}") from err

    async def create_batch_entries(
        self, entries: list[dict[str, Any]]
    ) -> dict[str, Any]:
        """Create multiple log entries in batch."""
        session = self._session
        try:
            async with session.post(
                f"{self._rust_api_url}/api/v1/logs/batch",
                json=entries,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=60),
            ) as response:
                data = await response.json()

                if response.status == 401:
                    raise MyLogAuthError(data.get("error", "Authentication failed"))
                if response.status >= 400:
                    raise MyLogApiError(
                        data.get("error", f"API error: {response.status}")
                    )

                return data
        except aiohttp.ClientError as err:
            raise MyLogConnectionError(f"Connection failed: {err}") from err

    async def _nuxt_get(self, path: str, params: dict | None = None) -> Any:
        """Make a GET request to the Nuxt Web API."""
        session = self._session
        try:
            async with session.get(
                f"{self._nuxt_api_url}{path}",
                params=params,
                headers=self._headers,
                timeout=aiohttp.ClientTimeout(total=15),
            ) as response:
                if response.status == 401:
                    raise MyLogAuthError("Authentication failed")
                if response.status >= 400:
                    raise MyLogApiError(f"API error: {response.status}")
                return await response.json()
        except aiohttp.ClientError as err:
            raise MyLogConnectionError(f"Connection failed: {err}") from err

    async def get_stats(self) -> dict[str, Any]:
        """Get dashboard statistics via the Nuxt API."""
        return await self._nuxt_get("/dashboard/stats")

    async def get_recent_entries(self, per_page: int = 5) -> dict[str, Any]:
        """Get recent log entries via the Nuxt API."""
        return await self._nuxt_get(
            "/logs",
            params={
                "perPage": per_page,
                "sortBy": "effectiveDate",
                "sortDesc": "true",
            },
        )

    async def get_log_types(self) -> list[dict[str, Any]]:
        """Get available log types via the Nuxt API."""
        return await self._nuxt_get("/log-types")

    async def get_tags(self) -> list[str]:
        """Get user's tags via the Nuxt API."""
        data = await self._nuxt_get("/tags")
        return data.get("tags", [])
