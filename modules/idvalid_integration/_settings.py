from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

from . import _constants

if TYPE_CHECKING:
    pass


__all__ = ("integration_settings",)


DEFAULTS = {}


REQUIRED = (
    _constants.CRYPTOGRAPHY_GRPC_SETTING_NAME,
    _constants.OTP_GRPC_SETTING_NAME,
    _constants.ENROLLMENT_GRPC_SETTING_NAME,
    _constants.AUTHN_GRPC_SETTINGS_NAME,
)


integration_settings = AppSetting(
    "IDVALID_INTEGRATION_SETTINGS",
    DEFAULTS,
    required=REQUIRED,
    check_required_immediately=True)
