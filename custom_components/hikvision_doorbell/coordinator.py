"""Data coordinator for Hikvision Doorbell."""
from __future__ import annotations

import asyncio
import logging
from typing import Any

import aiohttp
import async_timeout

from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DEFAULT_TIMEOUT

_LOGGER = logging.getLogger(__name__)


class HikvisionDoorbellCoordinator:
    """Class to manage fetching data from the middleware API."""

    def __init__(self, hass: HomeAssistant, middleware_url: str) -> None:
        """Initialize."""
        self.hass = hass
        self.middleware_url = middleware_url.rstrip("/")
        self._session = async_get_clientsession(hass)
        self._ws_to_device: aiohttp.ClientWebSocketResponse | None = None
        self._ws_from_device: aiohttp.ClientWebSocketResponse | None = None
        self._session_active = False

    async def async_test_connection(self) -> bool:
        """Test connection to middleware."""
        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.get(
                    f"{self.middleware_url}/api/channels"
                ) as response:
                    return response.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error connecting to middleware: %s", err)
            raise

    async def async_start_session(self) -> bool:
        """Start audio session on the middleware."""
        if self._session_active:
            _LOGGER.warning("Session already active")
            return True

        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.post(
                    f"{self.middleware_url}/api/session/start"
                ) as response:
                    if response.status == 200:
                        self._session_active = True
                        _LOGGER.info("Audio session started")
                        return True
                    else:
                        body = await response.text()
                        _LOGGER.error("Failed to start session: %s - %s", response.status, body)
                        return False
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error starting session: %s", err)
            return False

    async def async_stop_session(self) -> bool:
        """Stop audio session on the middleware."""
        if not self._session_active:
            _LOGGER.warning("No active session to stop")
            return True

        # Close WebSocket connections if open
        if self._ws_to_device:
            await self._ws_to_device.close()
            self._ws_to_device = None

        if self._ws_from_device:
            await self._ws_from_device.close()
            self._ws_from_device = None

        try:
            async with async_timeout.timeout(DEFAULT_TIMEOUT):
                async with self._session.post(
                    f"{self.middleware_url}/api/session/stop"
                ) as response:
                    self._session_active = False
                    _LOGGER.info("Audio session stopped")
                    return response.status == 200
        except (asyncio.TimeoutError, aiohttp.ClientError) as err:
            _LOGGER.error("Error stopping session: %s", err)
            self._session_active = False
            return False

    async def async_connect_to_device_ws(self) -> aiohttp.ClientWebSocketResponse:
        """Connect to WebSocket for sending audio to device."""
        if self._ws_to_device and not self._ws_to_device.closed:
            return self._ws_to_device

        ws_url = self.middleware_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/audio/to-device"

        try:
            self._ws_to_device = await self._session.ws_connect(ws_url)
            _LOGGER.info("Connected to to-device WebSocket")
            return self._ws_to_device
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to to-device WebSocket: %s", err)
            raise

    async def async_connect_from_device_ws(self) -> aiohttp.ClientWebSocketResponse:
        """Connect to WebSocket for receiving audio from device."""
        if self._ws_from_device and not self._ws_from_device.closed:
            return self._ws_from_device

        ws_url = self.middleware_url.replace("http://", "ws://").replace("https://", "wss://")
        ws_url = f"{ws_url}/api/audio/from-device"

        try:
            self._ws_from_device = await self._session.ws_connect(ws_url)
            _LOGGER.info("Connected to from-device WebSocket")
            return self._ws_from_device
        except aiohttp.ClientError as err:
            _LOGGER.error("Error connecting to from-device WebSocket: %s", err)
            raise

    async def async_send_audio_data(self, audio_data: bytes) -> bool:
        """Send audio data to device via WebSocket."""
        try:
            ws = await self.async_connect_to_device_ws()
            await ws.send_bytes(audio_data)
            return True
        except (aiohttp.ClientError, ConnectionError) as err:
            _LOGGER.error("Error sending audio data: %s", err)
            return False
