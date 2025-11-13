"""Data coordinator for Hikvision Doorbell."""
from __future__ import annotations

import asyncio
import logging

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class HikvisionDoorbellCoordinator:
    """Class to manage communication with the Hikvision Doorbell Server."""

    def __init__(self, hass: HomeAssistant, server_url: str) -> None:
        """Initialize."""
        self.hass = hass
        self.server_url = server_url.rstrip("/")
        self._session = async_get_clientsession(hass)

    async def async_test_connection(self) -> bool:
        """Test connection to server."""
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.get(
                    f"{self.server_url}/healthz"
                ) as response:
                    return response.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error connecting to server: %s", err)
            raise

    async def async_send_audio_file(self, audio_file_path: str) -> bool:
        """Send audio file to doorbell via play-file endpoint.

        The server handles session management automatically.
        Audio file will be converted to G.711 µ-law if needed.
        """
        try:
            # Read the audio file
            with open(audio_file_path, "rb") as f:
                audio_data = f.read()

            # Create multipart form data
            form_data = aiohttp.FormData()
            form_data.add_field(
                "audio",
                audio_data,
                filename="audio_file",
                content_type="application/octet-stream",
            )

            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.post(
                    f"{self.server_url}/api/audio/play-file",
                    data=form_data,
                ) as response:
                    if response.status == 200:
                        _LOGGER.info("Audio file sent successfully")
                        return True
                    else:
                        body = await response.text()
                        _LOGGER.error(
                            "Failed to send audio file: %s - %s", response.status, body
                        )
                        return False
        except (asyncio.TimeoutError, aiohttp.ClientError, OSError) as err:
            _LOGGER.error("Error sending audio file: %s", err)
            return False

    async def async_abort_operations(self) -> bool:
        """Abort all active operations (play-file and WebRTC sessions).

        This will:
        - Cancel any ongoing play-file operations
        - Close all WebRTC sessions
        - Release all audio channels on the doorbell
        """
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.post(
                    f"{self.server_url}/api/abort"
                ) as response:
                    if response.status == 200:
                        _LOGGER.info("All operations aborted successfully")
                        return True
                    else:
                        body = await response.text()
                        _LOGGER.error(
                            "Failed to abort operations: %s - %s", response.status, body
                        )
                        return False
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error aborting operations: %s", err)
            return False
