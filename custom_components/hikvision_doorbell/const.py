"""Constants for the Hikvision Doorbell integration."""

DOMAIN = "hikvision_doorbell"

# Configuration
CONF_SERVER_URL = "server_url"
CONF_RTSP_URL = "rtsp_url"

# Services
SERVICE_SEND_FILE = "send_file"

# Service attributes
ATTR_AUDIO_FILE = "audio_file"

# Default values
DEFAULT_NAME = "Hikvision Doorbell"
DEFAULT_TIMEOUT = 30  # Increased timeout for file uploads
