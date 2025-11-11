"""The Hikvision Doorbell Two-Way Audio integration."""
from __future__ import annotations

import logging
import os
from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant, ServiceCall
from homeassistant.exceptions import ConfigEntryNotReady, HomeAssistantError
import homeassistant.helpers.config_validation as cv

from .const import (
    ATTR_AUDIO_FILE,
    DOMAIN,
    SERVICE_SEND_FILE,
)
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CAMERA]

SERVICE_SEND_FILE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required(ATTR_AUDIO_FILE): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hikvision Doorbell from a config entry."""
    server_url = entry.data[CONF_HOST]

    coordinator = HikvisionDoorbellCoordinator(hass, server_url)

    # Test connection to server
    try:
        await coordinator.async_test_connection()
    except Exception as err:
        _LOGGER.error("Failed to connect to server: %s", err)
        raise ConfigEntryNotReady(f"Cannot connect to server at {server_url}") from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    # Register Lovelace resource for custom card
    _register_lovelace_resource(hass)

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register service
    async def handle_send_file(call: ServiceCall) -> None:
        """Handle send_file service call.

        Sends an audio file to the doorbell speaker.
        The server automatically handles session management and audio conversion.
        """
        coordinator = _get_coordinator_from_entity(hass, call.data["entity_id"])
        audio_file = call.data[ATTR_AUDIO_FILE]

        # Ensure file exists and is readable
        if not os.path.isfile(audio_file):
            raise HomeAssistantError(f"Audio file not found: {audio_file}")

        # Send audio file (server handles conversion and session management)
        if not await coordinator.async_send_audio_file(audio_file):
            raise HomeAssistantError("Failed to send audio file")

    hass.services.async_register(
        DOMAIN, SERVICE_SEND_FILE, handle_send_file, schema=SERVICE_SEND_FILE_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    # Unregister service if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_SEND_FILE)

    return unload_ok


def _get_coordinator_from_entity(hass: HomeAssistant, entity_id: str) -> HikvisionDoorbellCoordinator:
    """Get coordinator from entity_id."""
    # Extract entry_id from entity registry
    entity_registry = hass.helpers.entity_registry.async_get(hass)
    entity_entry = entity_registry.async_get(entity_id)

    if not entity_entry:
        raise HomeAssistantError(f"Entity not found: {entity_id}")

    return hass.data[DOMAIN][entity_entry.config_entry_id]


def _register_lovelace_resource(hass: HomeAssistant) -> None:
    """Register the custom Lovelace card resource."""
    # The card will be available at:
    # /local/community/hikvision_doorbell/hikvision-doorbell-card.js
    # Users need to add it manually to their Lovelace resources or use HACS
    _LOGGER.info(
        "Hikvision Doorbell custom card is available. "
        "Add the following resource to your Lovelace dashboard:\n"
        "URL: /hacsfiles/hikvision_doorbell/hikvision-doorbell-card.js\n"
        "Type: JavaScript Module"
    )
