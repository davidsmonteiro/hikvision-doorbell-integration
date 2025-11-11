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

from .const import CONF_MIDDLEWARE_URL, CONF_RTSP_URL, DOMAIN
from .coordinator import HikvisionDoorbellCoordinator

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_MIDDLEWARE_URL, default="http://localhost:8080"): str,
        vol.Optional(CONF_RTSP_URL): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect."""
    coordinator = HikvisionDoorbellCoordinator(hass, data[CONF_MIDDLEWARE_URL])

    try:
        await coordinator.async_test_connection()
    except Exception as err:
        _LOGGER.error("Cannot connect to middleware: %s", err)
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
                # Store middleware_url as CONF_HOST for coordinator
                data = {
                    CONF_HOST: user_input[CONF_MIDDLEWARE_URL],
                }
                if CONF_RTSP_URL in user_input:
                    data[CONF_RTSP_URL] = user_input[CONF_RTSP_URL]

                return self.async_create_entry(title=info["title"], data=data)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""
