from __future__ import annotations

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult

from .tonal_api import TonalAPI
from . import DOMAIN


class TonalConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for the Tonal integration."""

    VERSION = 1

    async def async_step_user(self, user_input=None) -> FlowResult:
        """Handle the initial step where the user enters credentials."""

        errors = {}

        if user_input is not None:
            email = user_input["email"]
            password = user_input["password"]

            # Prevent adding the integration twice
            await self.async_set_unique_id(email)
            self._abort_if_unique_id_configured()

            # Validate credentials by attempting a login
            api = TonalAPI(email, password)

            try:
                # Run authentication in executor thread
                await self.hass.async_add_executor_job(api._authenticate)
            except Exception:
                errors["base"] = "auth_failed"
            else:
                # Success — create the config entry
                return self.async_create_entry(
                    title=f"Tonal ({email})",
                    data={
                        "email": email,
                        "password": password,
                    },
                )

        # Show the form
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema(
                {
                    vol.Required("email"): str,
                    vol.Required("password"): str,
                }
            ),
            errors=errors,
        )