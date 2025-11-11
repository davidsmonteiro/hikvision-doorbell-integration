"""Camera platform for Hikvision Doorbell."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.camera import Camera, CameraEntityFeature
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from .const import CONF_RTSP_URL, DEFAULT_NAME, DOMAIN
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Hikvision Doorbell camera from a config entry."""
    coordinator: HikvisionDoorbellCoordinator = hass.data[DOMAIN][config_entry.entry_id]
    rtsp_url = config_entry.data.get(CONF_RTSP_URL)

    async_add_entities([HikvisionDoorbellCamera(coordinator, config_entry.entry_id, rtsp_url)])


class HikvisionDoorbellCamera(Camera):
    """Representation of a Hikvision Doorbell Camera with two-way audio."""

    _attr_has_entity_name = True
    _attr_name = None
    _attr_supported_features = CameraEntityFeature.STREAM

    def __init__(
        self,
        coordinator: HikvisionDoorbellCoordinator,
        entry_id: str,
        rtsp_url: str | None,
    ) -> None:
        """Initialize the camera."""
        super().__init__()
        self._coordinator = coordinator
        self._attr_unique_id = f"{entry_id}_camera"
        self._rtsp_url = rtsp_url

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
        """Return the RTSP stream source."""
        return self._rtsp_url

    async def async_camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return a still image from the camera."""
        # For RTSP cameras, Home Assistant will extract a frame from the stream
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
        }
