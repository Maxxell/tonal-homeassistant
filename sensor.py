from __future__ import annotations

from homeassistant.components.sensor import SensorEntity
from homeassistant.helpers.update_coordinator import CoordinatorEntity
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry

from . import DOMAIN


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities
):
    """Set up Tonal strength score sensors."""
    coordinator = hass.data[DOMAIN][entry.entry_id]

    sensors = []

    # coordinator.data is the dict returned by TonalAPI.fetch_data()
    # Example:
    # {
    #   "Quads": {"score": 1712, "region": "Lower Body", "updatedAt": "..."},
    #   "Chest": {...},
    #   ...
    # }
    for muscle_name, details in coordinator.data.items():
        sensors.append(TonalStrengthSensor(coordinator, muscle_name))

    async_add_entities(sensors)


class TonalStrengthSensor(CoordinatorEntity, SensorEntity):
    """Representation of a single Tonal muscle strength score sensor."""

    _attr_native_unit_of_measurement = "points"
    _attr_icon = "mdi:dumbbell"

    def __init__(self, coordinator, muscle_name: str):
        super().__init__(coordinator)
        self._muscle = muscle_name

        # Example: "Tonal Quads Strength Score"
        self._attr_name = f"Tonal {muscle_name} Strength Score"

        # Unique ID ensures HA doesn't duplicate sensors
        self._attr_unique_id = f"tonal_strength_{muscle_name.lower()}"

    @property
    def native_value(self):
        """Return the strength score."""
        data = self.coordinator.data.get(self._muscle)
        if not data:
            return None
        return data.get("score")

    @property
    def extra_state_attributes(self):
        """Return additional attributes: region + updatedAt."""
        data = self.coordinator.data.get(self._muscle)
        if not data:
            return {}
        return {
            "region": data.get("region"),
            "updatedAt": data.get("updatedAt"),
        }