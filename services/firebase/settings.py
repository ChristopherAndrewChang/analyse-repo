from __future__ import annotations
from typing import TYPE_CHECKING

from evercore.settings import AppSetting

if TYPE_CHECKING:
    pass


__all__ = ("firebase_settings",)


DEFAULTS = {
    "KEY_JSON_FILE": "",
}


firebase_settings = AppSetting(
    "IDVALID_FIREBASE_SETTINGS",
    DEFAULTS,
)