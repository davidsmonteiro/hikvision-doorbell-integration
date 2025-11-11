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
    SERVICE_START_2WAY,
    SERVICE_STOP_2WAY,
)
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)

PLATFORMS: list[Platform] = [Platform.CAMERA]

SERVICE_START_2WAY_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
    }
)

SERVICE_STOP_2WAY_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
    }
)

SERVICE_SEND_FILE_SCHEMA = vol.Schema(
    {
        vol.Required("entity_id"): cv.entity_id,
        vol.Required(ATTR_AUDIO_FILE): cv.string,
    }
)


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hikvision Doorbell from a config entry."""
    middleware_url = entry.data[CONF_HOST]

    coordinator = HikvisionDoorbellCoordinator(hass, middleware_url)

    # Test connection to middleware
    try:
        await coordinator.async_test_connection()
    except Exception as err:
        _LOGGER.error("Failed to connect to middleware: %s", err)
        raise ConfigEntryNotReady(f"Cannot connect to middleware at {middleware_url}") from err

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    # Register services
    async def handle_start_2way(call: ServiceCall) -> None:
        """Handle start_2way service call."""
        coordinator = _get_coordinator_from_entity(hass, call.data["entity_id"])
        if not await coordinator.async_start_session():
            raise HomeAssistantError("Failed to start two-way audio session")

    async def handle_stop_2way(call: ServiceCall) -> None:
        """Handle stop_2way service call."""
        coordinator = _get_coordinator_from_entity(hass, call.data["entity_id"])
        if not await coordinator.async_stop_session():
            raise HomeAssistantError("Failed to stop two-way audio session")

    async def handle_send_file(call: ServiceCall) -> None:
        """Handle send_file service call."""
        coordinator = _get_coordinator_from_entity(hass, call.data["entity_id"])
        audio_file = call.data[ATTR_AUDIO_FILE]

        # Ensure file exists and is readable
        if not os.path.isfile(audio_file):
            raise HomeAssistantError(f"Audio file not found: {audio_file}")

        # Read audio file
        try:
            with open(audio_file, "rb") as f:
                audio_data = f.read()
        except Exception as err:
            raise HomeAssistantError(f"Failed to read audio file: {err}") from err

        # Send audio data
        if not await coordinator.async_send_audio_data(audio_data):
            raise HomeAssistantError("Failed to send audio data")

    hass.services.async_register(
        DOMAIN, SERVICE_START_2WAY, handle_start_2way, schema=SERVICE_START_2WAY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_STOP_2WAY, handle_stop_2way, schema=SERVICE_STOP_2WAY_SCHEMA
    )
    hass.services.async_register(
        DOMAIN, SERVICE_SEND_FILE, handle_send_file, schema=SERVICE_SEND_FILE_SCHEMA
    )

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        hass.data[DOMAIN].pop(entry.entry_id)

    # Unregister services if this is the last entry
    if not hass.data[DOMAIN]:
        hass.services.async_remove(DOMAIN, SERVICE_START_2WAY)
        hass.services.async_remove(DOMAIN, SERVICE_STOP_2WAY)
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
