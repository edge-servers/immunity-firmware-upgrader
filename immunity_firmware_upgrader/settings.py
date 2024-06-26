from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.utils.module_loading import import_string

from immunity_controller.connection import settings as conn_settings

CUSTOM_OPENWRT_IMAGES = getattr(settings, 'IMMUNITY
_CUSTOM_OPENWRT_IMAGES', None)
# fmt: off
UPGRADERS_MAP = getattr(settings, 'IMMUNITY
_FIRMWARE_UPGRADERS_MAP', {
    conn_settings.DEFAULT_UPDATE_STRATEGIES[0][0]: 'immunity_firmware_upgrader.upgraders.openwrt.OpenWrt',
    conn_settings.DEFAULT_UPDATE_STRATEGIES[1][0]: 'immunity_firmware_upgrader.upgraders.immunity.Immunity
1'
})
# fmt: on

MAX_FILE_SIZE = getattr(
    settings, 'IMMUNITY
_FIRMWARE_UPGRADER_MAX_FILE_SIZE', 30 * 1024 * 1024
)

RETRY_OPTIONS = getattr(
    settings,
    'IMMUNITY
_FIRMWARE_UPGRADER_RETRY_OPTIONS',
    dict(max_retries=4, retry_backoff=60, retry_backoff_max=600, retry_jitter=True),
)

TASK_TIMEOUT = getattr(settings, 'IMMUNITY
_FIRMWARE_UPGRADER_TASK_TIMEOUT', 1500)

FIRMWARE_UPGRADER_API = getattr(settings, 'IMMUNITY
_FIRMWARE_UPGRADER_API', True)
FIRMWARE_API_BASEURL = getattr(settings, 'IMMUNITY
_FIRMWARE_API_BASEURL', '/')
OPENWRT_SETTINGS = getattr(settings, 'IMMUNITY
_FIRMWARE_UPGRADER_OPENWRT_SETTINGS', {})

# Path of urls that need to be refered in migrations files.
IMAGE_URL_PATH = 'firmware/'

try:
    PRIVATE_STORAGE_INSTANCE = import_string(
        getattr(
            settings,
            'IMMUNITY
_FIRMWARE_PRIVATE_STORAGE_INSTANCE',
            'immunity_firmware_upgrader.private_storage.storage.file_system_private_storage',
        )
    )
except ImportError:
    raise ImproperlyConfigured(
        'Failed to import FIRMWARE_UPGRADER_PRIVATE_STORAGE_INSTANCE'
    )