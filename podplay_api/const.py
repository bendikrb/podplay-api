"""podplay_api constants."""

import logging

PODPLAY_USER_AGENT = "podplay_api/0.0.0"
PODPLAY_API_URL = "https://api.podplay.com/v1"
PODPLAY_IMAGE_URL = "https://podplay.imgix.net"

IMAGE_WIDTHS = [300, 600, 960, 1280, 1600, 1920]

TIMEOUT = 10

LOGGER = logging.getLogger(__package__)
