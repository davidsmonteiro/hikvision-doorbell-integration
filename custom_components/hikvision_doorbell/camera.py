"""Camera platform for Hikvision Doorbell."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_FRIGATE_URL, CONF_CAMERA_NAME, DEFAULT_NAME, DOMAIN
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hikvision Doorbell camera from a config entry."""
    coordinator: HikvisionDoorbellCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    frigate_url = config_entry.data.get(CONF_FRIGATE_URL)
    camera_name = config_entry.data.get(CONF_CAMERA_NAME)

    async_add_entities([HikvisionDoorbellCamera(coordinator, config_entry.entry_id, frigate_url, camera_name)])


class HikvisionDoorbellCamera(Camera):
    """Representation of a Hikvision Doorbell Camera with two-way audio."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: HikvisionDoorbellCoordinator,
        entry_id: str,
        frigate_url: str | None,
        camera_name: str | None,
    ) -> None:
        """Initialize the camera."""
        super().__init__()
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry_id}_camera"
        self._frigate_url = frigate_url
        self._camera_name = camera_name

    @property
    def device_info(self):
        """Return device information."""
        return {
            "identifiers": {(DOMAIN, self._coordinator.server_url)},
            "name": DEFAULT_NAME,
            "manufacturer": "Hikvision",
            "model": "Doorbell",
        }

    async def stream_source(self) -> str | None:
        """Return the stream source - not used since we use Frigate/go2rtc."""
        return None

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        # Camera image will be fetched from Frigate
        return None

    @property
    def is_on(self) -> bool:
        """Return true if camera is on."""
        return True

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return extra state attributes."""
        return {
            "server_url": self._coordinator.server_url,
            "frigate_url": self._frigate_url,
            "camera_name": self._camera_name,
        }
