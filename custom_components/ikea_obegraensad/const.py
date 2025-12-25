"""Constants for the Ikea Obegraensad integration."""
from typing import Final

DOMAIN: Final = "ikea_obegraensad"

# Default values
DEFAULT_PORT: Final = 80
DEFAULT_TIMEOUT: Final = 5
DEFAULT_SCAN_INTERVAL: Final = 30

# API endpoints
API_STATUS: Final = "/api/status"
API_SET_DISPLAY: Final = "/api/setDisplay"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_NAME: Final = "name"

