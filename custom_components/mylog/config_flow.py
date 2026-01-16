"""Config flow for MyLog integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.data_entry_flow import FlowResult

from .api import MyLogApi, MyLogApiError, MyLogAuthError, MyLogConnectionError
from .const import DOMAIN


class MyLogConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for MyLog."""

    VERSION = 1

    async def async_step_user(self, user_input: dict | None = None) -> FlowResult:
        """Handle the initial step - API key entry."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api_key = user_input[CONF_API_KEY].strip()

            # Validate API key format
            if not api_key.startswith("mlk_"):
                errors["base"] = "invalid_api_key_format"
            else:
                # Check if already configured
                await self.async_set_unique_id(api_key)
                self._abort_if_unique_id_configured()

                # Test the API key
                api = MyLogApi(api_key)
                try:
                    await api.health_check()

                    # Create the config entry
                    return self.async_create_entry(
                        title="MyLog",
                        data={CONF_API_KEY: api_key},
                    )
                except MyLogAuthError:
                    errors["base"] = "invalid_auth"
                except MyLogConnectionError:
                    errors["base"] = "cannot_connect"
                except MyLogApiError:
                    errors["base"] = "unknown"
                finally:
                    await api.close()

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required(CONF_API_KEY): str,
                }
            ),
            errors=errors,
            description_placeholders={
                "mylog_url": "https://mylog.zip",
            },
        )
