"""Config flow for Hikvision Doorbell integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError

from .const import CONF_SERVER_URL, CONF_FRIGATE_URL, CONF_CAMERA_NAME, DOMAIN
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_SERVER_URL): str,
        vol.Required(CONF_FRIGATE_URL): str,
        vol.Required(CONF_CAMERA_NAME): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    coordinator = HikvisionDoorbellCoordinator(hass, data[CONF_SERVER_URL])

    try:
        await coordinator.async_test_connection()
    except Exception as err:
        _LOGGER.error("Cannot connect to server: %s", err)
        raise CannotConnect from err

    return {"title": "Hikvision Doorbell"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hikvision Doorbell."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)
            except CannotConnect:
                errors["base"] = "cannot_connect"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"
            else:
                # Store configuration
                data = {
                    CONF_HOST: user_input[CONF_SERVER_URL],
                    CONF_FRIGATE_URL: user_input[CONF_FRIGATE_URL],
                    CONF_CAMERA_NAME: user_input[CONF_CAMERA_NAME],
                }

                return self.async_create_entry(title=info["title"], data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
