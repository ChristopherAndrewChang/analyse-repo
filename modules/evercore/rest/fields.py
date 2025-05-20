from __future__ import annotations
from typing import TYPE_CHECKING

import base64
import binascii
import logging

from django.core.validators import (
    MaxLengthValidator,
    MinLengthValidator,
)
from django.utils.translation import gettext_lazy as _

from rest_framework.fields import Field, empty
from rest_framework.utils.formatting import lazy_format

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__alL__ = ("BinaryField", "Base64Field")


base64_urlsafe_altchars = b'-_'


class BinaryField(Field):
    default_error_messages = {
        'invalid': _('Not a valid string.'),
        'invalid_unicode': _("Not a valid {encoding} encoding characters."),
        'blank': _('This field may not be blank.'),
        # 'even_length': _('Ensure this field has even characters length.'),
        'max_length': _(
            'Ensure this field has no more than {max_length} bytes length.'),
        'min_length': _(
            'Ensure this field has at least {min_length} bytes length.'),
    }
    default_encoding = 'utf-8'

    def __init__(self, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        self.base64_urlsafe = kwargs.pop('base64_urlsafe', True)
        self.base64_format = kwargs.pop('base64_format', True)
        encoding = kwargs.pop('encoding', self.default_encoding)
        if encoding is None:
            encoding = self.default_encoding
        self.encoding = encoding

        # validate encoding
        import codecs
        try:
            codecs.lookup(self.encoding)
        except LookupError:
            raise AssertionError(f"Invalid encoding `{encoding}`.")

        super().__init__(**kwargs)

        if self.max_length is not None:
            message = lazy_format(
                self.error_messages['max_length'],
                max_length=self.max_length)
            self.validators.append(
                MaxLengthValidator(self.max_length, message=message))

        if self.min_length is not None:
            message = lazy_format(
                self.error_messages['min_length'],
                min_length=self.min_length)
            self.validators.append(
                MinLengthValidator(self.min_length, message=message))

    def run_validation(self, data=empty) -> bytes:
        # handle blank
        if isinstance(data, bytes):
            if data == b'' or (self.trim_whitespace and (data.strip()) == b''):
                if not self.allow_blank:
                    self.fail('blank')
                return b''
        else:
            if data == '' or (self.trim_whitespace and str(data).strip() == ''):
                if not self.allow_blank:
                    self.fail('blank')
                return b''
        return super().run_validation(data)

    def to_internal_value(self, data: str) -> bytes:
        if isinstance(data, bytes):
            return data.strip() if self.trim_whitespace else data

        if not isinstance(data, str):
            self.fail('invalid')
        data = data.strip() if self.trim_whitespace else data

        if not self.base64_format:
            try:
                return data.encode(self.encoding)
            except UnicodeEncodeError:
                self.fail('invalid_unicode', encoding=self.encoding)
        try:
            return base64.b64decode(
                data, altchars=(
                    base64_urlsafe_altchars
                    if self.base64_urlsafe else
                    None
                ), validate=True
            )
        except (binascii.Error, ValueError):
            self.fail('invalid_unicode', encoding='base64')

    def to_representation(self, value: bytes) -> str:
        if isinstance(value, str):
            return value

        if not self.base64_format:
            try:
                return value.decode(self.encoding)
            except UnicodeEncodeError:
                # use base64 encoding as fallback
                pass
        return base64.b64encode(
            value, altchars=(
                base64_urlsafe_altchars
                if self.base64_urlsafe else
                None
            )
        ).decode("ascii")


class Base64Field(Field):
    default_error_messages = {
        'blank': _('This field may not be blank.'),
        'invalid': _('Not a valid base64 string.'),
        # 'even_length': _('Ensure this field has even characters length.'),
        'max_length': _(
            'Ensure this field has no more than {max_length} bytes length.'),
        'min_length': _(
            'Ensure this field has at least {min_length} bytes length.'),
    }

    def __init__(self, **kwargs):
        self.allow_blank = kwargs.pop('allow_blank', False)
        self.trim_whitespace = kwargs.pop('trim_whitespace', True)
        self.max_length = kwargs.pop('max_length', None)
        self.min_length = kwargs.pop('min_length', None)
        self.urlsafe = kwargs.pop('urlsafe', False)
        self.strict = kwargs.pop('strict', True)
        self.remove_padding = kwargs.pop('remove_padding', False)
        super().__init__(**kwargs)

        if self.max_length is not None:
            message = lazy_format(
                self.error_messages['max_length'],
                max_length=self.max_length)
            self.validators.append(
                MaxLengthValidator(self.max_length, message=message))

        if self.min_length is not None:
            message = lazy_format(
                self.error_messages['min_length'],
                min_length=self.min_length)
            self.validators.append(
                MinLengthValidator(self.min_length, message=message))

    def run_validation(self, data=empty):
        is_blank = False
        if data is not empty:
            if isinstance(data, bytes):
                is_blank = (
                        data == b'' or (self.trim_whitespace and data.strip() == b'')
                )
            else:
                is_blank = (
                    data == '' or
                    (self.trim_whitespace and str(data).strip() == '')
                )

        if is_blank:
            if not self.allow_blank:
                self.fail('blank')
            return b''
        return super().run_validation(data)

    def to_internal_value(self, data):
        if isinstance(data, bytes):
            return data

        if not self.strict:
            if left := (len(data) % 4):
                data += "=" * (4 - left)
        try:
            return base64.b64decode(
                data,
                altchars=(
                    base64_urlsafe_altchars
                    if self.urlsafe else
                    None
                ),
                validate=True)
        except binascii.Error:
            self.fail("invalid")

    def to_representation(self, value):
        if not value:
            return None

        value = base64.b64encode(
            value,
            altchars=(
                base64_urlsafe_altchars
                if self.urlsafe else
                None
            )
        )
        if self.remove_padding:
            value.rstrip(b"=")
        return value.decode()
