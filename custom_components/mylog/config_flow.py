"""Config flow for MyLog integration."""
from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.const import CONF_API_KEY
from homeassistant.core import callback
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

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> MyLogOptionsFlowHandler:
        """Get the options flow for this handler."""
        return MyLogOptionsFlowHandler()


class MyLogOptionsFlowHandler(config_entries.OptionsFlow):
    """Handle MyLog options."""

    async def async_step_init(self, user_input: dict | None = None) -> FlowResult:
        """Handle sending a test message."""
        errors: dict[str, str] = {}

        if user_input is not None:
            api = MyLogApi(self.config_entry.data[CONF_API_KEY])
            try:
                await api.create_log_entry(
                    title=user_input.get("title", "Test from Home Assistant"),
                    content=user_input.get("content", "This is a test message from the MyLog integration."),
                    severity="info",
                    tags=["test", "home-assistant"],
                )
                return self.async_abort(reason="test_message_sent")
            except MyLogConnectionError:
                errors["base"] = "cannot_connect"
            except MyLogAuthError:
                errors["base"] = "invalid_auth"
            except MyLogApiError:
                errors["base"] = "unknown"
            finally:
                await api.close()

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional("title", default="Test from Home Assistant"): str,
                    vol.Optional(
                        "content",
                        default="This is a test message from the MyLog integration.",
                    ): str,
                }
            ),
            errors=errors,
        )
