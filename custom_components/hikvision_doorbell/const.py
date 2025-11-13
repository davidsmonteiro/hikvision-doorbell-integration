"""Constants for the Hikvision Doorbell integration."""

DOMAIN = "hikvision_doorbell"

# Configuration
CONF_SERVER_URL = "server_url"
CONF_FRIGATE_URL = "frigate_url"
CONF_CAMERA_NAME = "camera_name"

# Services
SERVICE_PLAY_FILE = "play_file"
SERVICE_ABORT = "abort"

# Service attributes
ATTR_AUDIO_FILE = "audio_file"

# Default values
DEFAULT_NAME = "Hikvision Doorbell"
DEFAULT_TIMEOUT = 30  # Increased timeout for file uploads
