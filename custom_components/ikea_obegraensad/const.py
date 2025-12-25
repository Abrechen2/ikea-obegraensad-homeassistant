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
API_SET_AUTO_BRIGHTNESS: Final = "/api/setAutoBrightness"
API_SET_TIMEZONE: Final = "/api/setTimezone"
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
KEY_AUTO_BRIGHTNESS_ENABLED: Final = "autoBrightnessEnabled"
KEY_AUTO_BRIGHTNESS_MIN: Final = "autoBrightnessMin"
KEY_AUTO_BRIGHTNESS_MAX: Final = "autoBrightnessMax"
KEY_AUTO_BRIGHTNESS_SENSOR_MIN: Final = "autoBrightnessSensorMin"
KEY_AUTO_BRIGHTNESS_SENSOR_MAX: Final = "autoBrightnessSensorMax"
KEY_TIMEZONE: Final = "timezone"

# Configuration keys
CONF_HOST: Final = "host"
CONF_PORT: Final = "port"
CONF_NAME: Final = "name"

# Brightness conversion
BRIGHTNESS_MAX_API: Final = 1023
BRIGHTNESS_MAX_HA: Final = 255

# Timezones (important/common timezones)
TIMEZONES: Final = [
    "UTC",
    "Europe/Berlin",
    "Europe/London",
    "Europe/Paris",
    "Europe/Rome",
    "Europe/Madrid",
    "Europe/Amsterdam",
    "Europe/Vienna",
    "Europe/Stockholm",
    "Europe/Zurich",
    "America/New_York",
    "America/Chicago",
    "America/Denver",
    "America/Los_Angeles",
    "America/Toronto",
    "America/Mexico_City",
    "America/Sao_Paulo",
    "Asia/Tokyo",
    "Asia/Shanghai",
    "Asia/Hong_Kong",
    "Asia/Dubai",
    "Asia/Singapore",
    "Australia/Sydney",
    "Australia/Melbourne",
    "Pacific/Auckland",
]

