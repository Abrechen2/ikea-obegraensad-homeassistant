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
API_SET_BRIGHTNESS: Final = "/api/setBrightness"
API_EFFECT: Final = "/effect"

# Effect names
EFFECTS: Final = [
    "snake",
    "clock",
    "rain",
    "bounce",
    "stars",
    "lines",
    "pulse",
    "waves",
    "spiral",
    "fire",
    "plasma",
    "ripple",
    "sandclock",
]

# Status data keys
KEY_DISPLAY_ENABLED: Final = "displayEnabled"
KEY_BRIGHTNESS: Final = "brightness"
KEY_CURRENT_EFFECT: Final = "currentEffect"
KEY_TIME: Final = "time"
KEY_PRESENCE: Final = "presence"
KEY_SENSOR_VALUE: Final = "sensorValue"
KEY_IP_ADDRESS: Final = "ipAddress"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_NAME: Final = "name"

# Brightness conversion
BRIGHTNESS_MAX_API: Final = 1023
BRIGHTNESS_MAX_HA: Final = 255

