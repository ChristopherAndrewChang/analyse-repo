from __future__ import annotations

import contextlib
from typing import TYPE_CHECKING

import base64
import datetime

from google.protobuf.message import Message
from google.protobuf.timestamp_pb2 import Timestamp
from google.protobuf.duration_pb2 import Duration

from django.core.validators import MaxLengthValidator, MinLengthValidator
from django.utils.translation import gettext_lazy as _

from rest_framework import fields, serializers
from rest_framework.utils.formatting import lazy_format

from phonenumber_field.serializerfields import PhoneNumberField

from evercore.rest.fields import BinaryField as rest_BinaryField

if TYPE_CHECKING:
    from typing import TypeVar
    FieldType_co = TypeVar("FieldType_co", covariant=True)


__all__ = (
    # Mixin types
    "ProtoFieldMixin",
    "ProtoBytesFieldMixin", "ProtoStringFieldMixin",
    "ProtoNumberFieldMixin", "ProtoIterableFieldMixin",
    # Base types
    "Field",
    # Boolean types
    "BooleanField",
    # String types
    "CharField", "EmailField", "RegexField", "SlugField",
    "URLField", "UUIDField", "IPAddressField", "PhoneNumberField",
    # Number types
    "IntegerField", "FloatField", "DecimalField",
    # Date & time types
    "DateTimeField", "DateField", "TimeField", "DurationField",
    # Choice types
    "OneOfField", "ChoiceField", "MultipleChoiceField", "FilePathField",
    # File types
    "FileField", "ImageField",
    # Composite field types
    "ListField", "DictField", "HStoreField", "JSONField",
    # Miscellaneous field types
    "ReadOnlyField", "SerializerMethodField", "ModelField",
    # Binary types
    "BinaryField",
)


def is_proto_wrapper(value) -> bool:
    return (
        isinstance(value, Message) and
        value.__class__.__module__ == "google.protobuf.wrappers_pb2")


class ProtoFieldMixin:
    field_name: "str"
    root: serializers.BaseSerializer | None
    default_empty_html: str | type[fields.empty]
    error_messages: dict
    required: bool
    allow_null: bool

    def __init__(
            self, *args,
            wrapped_input: bool = False, **kwargs):
        self.wrapped_input = wrapped_input
        super().__init__(*args, **kwargs)

    def get_value(self, dictionary: Message | dict):
        field_name = self.field_name
        if isinstance(dictionary, Message):
            try:
                # field has presence
                if dictionary.HasField(field_name):
                    # field is set
                    value = getattr(dictionary, field_name)
                else:
                    # field is not set
                    return fields.empty
            except ValueError:
                # field is scalar type or not defined
                # try to get directly
                try:
                    # scalar type has no wrapper except repeated or map.
                    value = getattr(dictionary, field_name)
                except AttributeError:
                    # field not defined
                    return fields.empty
                else:
                    # checking for possible null value
                    return self.decide_null(value)
            else:
                # no need to check null possibility. it should be set as needed
                # checking for wrapped value
                if self.wrapped_input and is_proto_wrapper(value):
                    return value.value
                return value
        return dictionary.get(self.field_name, fields.empty)

    def decide_null(self, value):
        return value


class ProtoBytesFieldMixin(ProtoFieldMixin):
    allow_blank: bool

    def decide_null(self, value):
        if not self.allow_blank and value in [b'', '']:
            if self.allow_null:
                return None
            if not self.required:
                return fields.empty
        return value


class ProtoStringFieldMixin(ProtoFieldMixin):
    allow_blank: bool

    def decide_null(self, value):
        if not self.allow_blank and value == '':
            if self.allow_null:
                return None
            if not self.required:
                return fields.empty
        return value


class ProtoNumberFieldMixin(ProtoFieldMixin):
    def __init__(
            self, *,
            allow_zero: bool = True, **kwargs):
        super().__init__(**kwargs)
        self.allow_zero = allow_zero

    def decide_null(self, value):
        if value == '':
            if not self.required:
                return fields.empty
            return None
        if not self.allow_zero and value == 0:
            if self.allow_null:
                return None
            if not self.required:
                return fields.empty
        return value


class ProtoIterableFieldMixin(ProtoFieldMixin):
    allow_empty: bool

    def decide_null(self, value):
        if not self.allow_empty and len(value) == 0:
            if self.allow_null:
                return None
            if not self.required:
                return fields.empty
        return value


class Field(ProtoFieldMixin, fields.Field):
    pass


# Boolean types...

class BooleanField(ProtoFieldMixin, fields.BooleanField):
    pass


# String types...

class CharField(ProtoStringFieldMixin, fields.CharField):
    pass


class EmailField(ProtoStringFieldMixin, fields.EmailField):
    pass


class RegexField(ProtoStringFieldMixin, fields.RegexField):
    pass


class SlugField(ProtoStringFieldMixin, fields.SlugField):
    pass


class URLField(ProtoStringFieldMixin, fields.URLField):
    pass


class UUIDField(ProtoFieldMixin, fields.UUIDField):
    pass


class IPAddressField(ProtoStringFieldMixin, fields.IPAddressField):
    pass


class PhoneNumberField(ProtoStringFieldMixin, PhoneNumberField):
    def __init__(self, **kwargs):
        # Based on ITU-T E.164 specification. The maximum total number of
        # digits is 15 (excluding `+`). So we extend 1 digit to include `+` char.
        # https://www.itu.int/ITU-D/treg/Events/Seminars/2010/Ghana10/pdf/Session2.pdf
        kwargs["max_length"] = 16
        kwargs["trim_whitespace"] = True
        super().__init__(**kwargs)


# Number types...


class IntegerField(ProtoNumberFieldMixin, fields.IntegerField):
    pass


class FloatField(ProtoNumberFieldMixin, fields.FloatField):
    pass


class DecimalField(ProtoNumberFieldMixin, fields.DecimalField):
    pass


# Date & time types...

class DateTimeField(ProtoFieldMixin, fields.DateTimeField):
    default_error_messages = {
        'invalid': _('Expected a google.protobuf.timestamp_pb2.Timestamp but got {format}'),
    }

    def to_internal_value(
            self, value: Timestamp | datetime.datetime
    ) -> datetime.datetime:
        if isinstance(value, Timestamp):
            return self.enforce_timezone(value.ToDatetime())

        if isinstance(value, datetime.date) and not isinstance(value, datetime.datetime):
            self.fail('date')

        if isinstance(value, datetime.datetime):
            return self.enforce_timezone(value)

        self.fail('invalid', format=type(value).__class__.__name__)

    # def to_representation(
    #         self, value: datetime.datetime | Timestamp
    # ) -> Timestamp | None:
    #     if not value:
    #         return None
    #
    #     if isinstance(value, Timestamp):
    #         return value
    #
    #     result = Timestamp()
    #     result.FromDatetime(
    #         self.enforce_timezone(value).astimezone(datetime.UTC))
    #     return result


class DateField(ProtoFieldMixin, fields.DateField):
    pass


class TimeField(ProtoFieldMixin, fields.TimeField):
    pass


class DurationField(ProtoFieldMixin, fields.DurationField):
    default_error_messages = {
        'invalid': _('Expected a google.protobuf.duration_pb2.Duration but got {format}'),
    }

    def to_internal_value(self, value: Duration | datetime.timedelta) -> datetime.timedelta:
        if isinstance(value, Duration):
            return value.ToTimedelta()

        if isinstance(value, datetime.timedelta):
            return value

        self.fail('invalid', format=type(value).__class__.__name__)

    def to_representation(self, value: datetime.timedelta | Duration) -> Duration | None:
        if not value:
            return None

        if isinstance(value, Duration):
            return value

        result = Duration()
        result.FromTimedelta(value)
        return result


# Choice types...


class OneOfField(ProtoFieldMixin, fields.Field):
    def __init__(self, fields_map: "dict[str, FieldType_co]", **kwargs):
        # noinspection Assert
        assert fields_map, "fields_map cannot be empty"
        kwargs["write_only"] = True
        super().__init__(**kwargs)
        self.fields_map = fields_map
        for key, val in fields_map.items():
            val.bind(field_name='', parent=self)

    def get_value(self, dictionary):
        if isinstance(dictionary, Message):
            for key, field in self.fields_map.items():
                with contextlib.suppress(ValueError):
                    if dictionary.HasField(key):
                        value = getattr(dictionary, key)
                        if self.wrapped_input and is_proto_wrapper(value):
                            value = field.decide_null(value.value)
                        else:
                            value = field.decide_null(value)
                        return key, value
            return fields.empty
        try:
            key = dictionary[self.field_name]
        except KeyError:
            return fields.empty
        else:
            return key, dictionary.get(key, fields.empty)

    def to_internal_value(self, data: tuple):
        key, data = data
        return self.run_child_validation(key, data)

    def run_child_validation(self, key: str, data):
        return key, self.fields_map[key].run_validation(data)


class ChoiceField(ProtoStringFieldMixin, fields.ChoiceField):
    pass


class MultipleChoiceField(ProtoIterableFieldMixin, fields.MultipleChoiceField):
    pass


class FilePathField(ProtoStringFieldMixin, fields.FilePathField):
    pass


# File types...

class FileField(ProtoFieldMixin, fields.FileField):
    pass


class ImageField(ProtoFieldMixin, fields.ImageField):
    pass


# Composite field types...

class _UnvalidatedField(Field):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.allow_blank = True
        self.allow_null = True

    def to_internal_value(self, data):
        return data

    def to_representation(self, value):
        return value


class ListField(ProtoIterableFieldMixin, fields.ListField):
    child = _UnvalidatedField()


class DictField(ProtoIterableFieldMixin, fields.DictField):
    child = _UnvalidatedField()


class HStoreField(ProtoIterableFieldMixin, fields.HStoreField):
    child = CharField(allow_blank=True, allow_null=True)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # noinspection Assert
        assert isinstance(self.child, CharField), (
            "The `child` argument must be an instance of `CharField`, "
            "as the hstore extension stores values as strings."
        )


class JSONField(ProtoStringFieldMixin, fields.JSONField):
    pass


# Miscellaneous field types...

class ReadOnlyField(ProtoFieldMixin, fields.ReadOnlyField):
    pass


class SerializerMethodField(ProtoFieldMixin, fields.SerializerMethodField):
    pass


class ModelField(ProtoFieldMixin, fields.ModelField):
    pass


class BinaryField(ProtoBytesFieldMixin, rest_BinaryField):
    pass
