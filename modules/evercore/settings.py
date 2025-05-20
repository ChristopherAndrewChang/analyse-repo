from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured
from django.core.signals import setting_changed
from django.utils.module_loading import import_string

if TYPE_CHECKING:
    from collections.abc import Sequence, Mapping
    from typing import Any


logger = logging.getLogger(__name__)
__all__ = ("perform_import", "import_from_string", "AppSetting")


def perform_import(val, setting_name: str | Sequence[str]) -> Any | Sequence[Any] | None:
    """
    If the given setting is a string import notation,
    then perform the necessary import or imports.
    """
    if val is None:
        return None
    elif isinstance(val, str):
        return import_from_string(val, setting_name)
    elif isinstance(val, (list, tuple)):
        return [import_from_string(item, setting_name) for item in val]
    return val


def import_from_string(val: str, setting_name: str) -> Any:
    """
    Attempt to import a class from a string representation.
    """
    try:
        return import_string(val)
    except ImportError as e:
        msg = "Could not import %r for setting %r. %s: %s." % (val, setting_name, e.__class__.__name__, e)
        raise ImportError(msg)


class AppSetting:
    """
    A settings object that allows app settings to be accessed as properties.

    Any setting with string import paths will be automatically resolved
    and return the class, rather than the string literal.
    """
    check_required: bool = False

    def __init__(
        self,
        setting_name: str, /,
        defaults: Mapping[str, Any], *,
        name: str = None,
        import_strings: Sequence[str] = None,
        mandatory: Sequence[str] = None,
        required: Sequence[str] = None,
        user_settings: dict = None,
        check_required_immediately: bool = False,
    ):
        """Application settings.

        Parameters
        ----------
        setting_name: str
            Setting name in django settings.
        defaults: Mapping[str, Any]
            Default settings.
        name: str, optional
            App setting name. If not provided will use `setting_name` as name.
        import_strings: Sequence[str], optional
            List of settings that need to be imported.
        mandatory: Sequence[str], optional
            List of mandatory settings. Mandatory settings should not be `None` in `user_settings`.
            And `defaults` must provide the default value for mandatory settings.
        required: Sequence[str], optional
            List of required settings. Required settings must be set in `user_settings`.
            `defaults` should not provide value for required settings.
        user_settings: Mapping[str, Any], optional
            User settings. If not provided, user settings will be collected from
            django settings using `setting_name` value.
        check_required_immediately: bool, optional
            If `True` will immediately check required settings in user settings.
            Otherwise, check will be performed lazily when accessing required settings.
        """
        self._cached_attrs = set()
        self.setting_name = setting_name
        self.defaults = defaults
        self.name = name or setting_name
        self._list_settings = list(defaults.keys())
        self.import_strings = import_strings or ()

        if mandatory:
            # make sure default provide all mandatory settings
            err_keys = []
            for key in mandatory:
                try:
                    val = defaults[key]
                except KeyError:
                    err_keys.append(key)
                else:
                    if val is None:
                        err_keys.append(key)
            if err_keys:
                keys = ", ".join(err_keys)
                raise ImproperlyConfigured(
                    f"`defaults` must provide all mandatory settings. "
                    f"Invalid keys {keys}."
                )
        self.mandatory = mandatory or ()

        if required:
            # make sure default not provide all required settings
            err_keys = []
            for key in required:
                if key in self.mandatory:
                    continue
                try:
                    defaults[key]
                except KeyError:
                    continue
                else:
                    err_keys.append(key)
            if err_keys:
                keys = ", ".join(err_keys)
                raise ImproperlyConfigured(
                    f"`defaults` should not provide all required settings. "
                    f"Invalid keys {keys} "
                )
            self.check_required = True
            self._list_settings.extend(required)
        self.required = required or ()

        if user_settings:
            self._user_settings = user_settings

        if check_required_immediately:
            self._pre_check()

        # connect signal
        setting_changed.connect(self._setting_changed)

    def __del__(self):
        # disconnect signal
        setting_changed.disconnect(self._setting_changed)

    def _setting_changed(self, *args, **kwargs):
        """ Setting changed signal receiver
        """
        setting = kwargs['setting']
        if setting == self.setting_name:
            self.reload()

    @property
    def user_settings(self) -> Mapping[str, Any]:
        """ Populate user settings

        Will be populated from django settings if not provided in `__init__`.

        Returns
        -------
        _user_settings: Mapping[str, Any]
            Populated user settings.
        """
        if not hasattr(self, "_user_settings"):
            self._user_settings = getattr(settings, self.setting_name, {})
        return self._user_settings

    def _pre_check(self):
        """ Pre-check required settings

        Check required setting in user setting. It is also check for mandatory setting if
        the required setting registered as mandatory.
        """
        if not self.check_required:
            # no required provided
            return

        required_keys = []
        mandatory_keys = []
        user_settings = self.user_settings
        for key in self.required:
            try:
                val = user_settings[key]
            except KeyError:
                required_keys.append(key)
            else:
                # check for mandatory
                if key in self.mandatory and not val:
                    mandatory_keys.append(key)

        if required_keys:
            keys = ", ".join(required_keys)
            raise ImproperlyConfigured(
                f"These settings must be provided in {self.setting_name}. "
                f"Settings `{keys}`")
        if mandatory_keys:
            keys = ". ".join(mandatory_keys)
            raise ImproperlyConfigured(
                f"These settings are mandatory. "
                f"Settings `{keys}`")

        self.check_required = False

    def __getattr__(self, attr):
        if attr not in self._list_settings:
            raise AttributeError(f"Invalid {self.name} settings: `{attr}`")

        try:
            # Check if present in user settings
            val = self.user_settings[attr]
        except KeyError:
            # Check if required
            if self.check_required and attr in self.required:
                # required setting not provided
                raise AttributeError(
                    f"{self.name} settings: `{attr}` is required")
            # Fall back to defaults
            val = self.defaults[attr]

        if val and attr in self.import_strings:
            val = perform_import(val, attr)

        self.validate_setting(attr, val)

        # Cache the result
        self._cached_attrs.add(attr)
        setattr(self, attr, val)
        return val

    def reload(self):
        """ Reload setting

        Remove all cached attributes and user settings
        """
        for attr in self._cached_attrs:
            delattr(self, attr)
        self._cached_attrs.clear()
        if hasattr(self, '_user_settings'):
            delattr(self, '_user_settings')

    def validate_setting(self, attr: str, val: Any):
        """ Validate setting

        Validate setting value. Currently, only validate for mandatory value

        Parameters
        ----------
        attr: str
            setting name.
        val: Any
            setting value.
        """
        if not val and attr in self.mandatory:
            raise ImproperlyConfigured(
                f"{self.name} settings: `{attr}` is mandatory")
