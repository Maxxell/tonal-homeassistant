from __future__ import annotations

import logging
from datetime import timedelta

from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import (
    DataUpdateCoordinator,
    UpdateFailed,
)

from .tonal_api import TonalAPI

_LOGGER = logging.getLogger(__name__)

DOMAIN = "tonal"
PLATFORMS = ["sensor"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Set up the Tonal integration from a config entry."""

    email = entry.data["email"]
    password = entry.data["password"]

    api = TonalAPI(email, password)

    async def async_update_data():
        """Fetch data from Tonal API."""
        try:
            # Run the blocking API call in the executor thread
            return await hass.async_add_executor_job(api.fetch_data)
        except Exception as err:
            raise UpdateFailed(f"Tonal update failed: {err}") from err

    coordinator = DataUpdateCoordinator(
        hass,
        _LOGGER,
        name="tonal_strength_scores",
        update_method=async_update_data,
        update_interval=timedelta(hours=6),
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Store coordinator so sensor.py can access it
    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Forward setup to sensor platform
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry):
    """Unload a config entry."""
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)

    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok