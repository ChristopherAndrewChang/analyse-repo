from __future__ import annotations
from typing import TYPE_CHECKING

from google.protobuf.message import Message

from django.utils.functional import cached_property

from rest_framework.serializers import (
    BaseSerializer, Serializer, ListSerializer, ModelSerializer,
    LIST_SERIALIZER_KWARGS, LIST_SERIALIZER_KWARGS_REMOVE, empty, Field
)
from rest_framework.settings import api_settings
from rest_framework.exceptions import ValidationError

from evercore_grpc.protobuf.json_format import message_to_dict, parse_dict


if TYPE_CHECKING:
    type InitialDataTypes = dict | "Message" | bytes | list
    from typing import Callable, Any


class ProtoSerializerMixin:
    initial_data: "InitialDataTypes"
    run_validation: "Callable[[InitialDataTypes | empty], Any]"

    @cached_property
    def write_proto_cls(self) -> type[Message] | None:
        try:
            meta = getattr(self, 'Meta')
        except AttributeError:
            return None
        try:
            return getattr(meta, 'write_proto_class')
        except AttributeError:
            return getattr(meta, 'proto_class', None)

    @cached_property
    def read_proto_cls(self) -> type[Message] | None:
        try:
            meta = getattr(self, 'Meta')
        except AttributeError:
            return None
        try:
            return getattr(meta, 'read_proto_class')
        except AttributeError:
            return getattr(meta, 'proto_class', None)

    def convert_initial_data(self):
        data = self.initial_data
        if isinstance(data, bytes):
            proto_cls = self.read_proto_cls
            # noinspection Assert
            assert proto_cls is not None, (
                f'Class {self.__class__.__name__} must provide '
                f'"Meta.write_proto_class" or "Meta.proto_class" attribute '
                f'to convert raw message')
            return

    def is_valid(self, *, raise_exception=False):
        assert hasattr(self, 'initial_data'), (
            'Cannot call `.is_valid()` as no `data=` keyword argument was '
            'passed when instantiating the serializer instance.'
        )

        if not hasattr(self, '_validated_data'):
            try:
                self._validated_data = self.run_validation(self.initial_data)
            except ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)


class BaseProtoSerializer(BaseSerializer):
    def __init__(self, instance=None, message: Message | bytes = empty, **kwargs):
        if message is not empty:
            self.initial_message = message
            kwargs['data'] = self.message_to_data(message)
        super().__init__(instance, **kwargs)

    def get_write_proto_cls(self) -> type[Message] | None:
        try:
            meta = getattr(self, 'Meta')
        except AttributeError:
            return None
        try:
            return getattr(meta, 'write_proto_class')
        except AttributeError:
            return getattr(meta, 'proto_class', None)

    def get_read_proto_cls(self) -> type[Message] | None:
        try:
            meta = getattr(self, 'Meta')
        except AttributeError:
            return None
        try:
            return getattr(meta, 'read_proto_class')
        except AttributeError:
            return getattr(meta, 'proto_class', None)

    def message_to_data(self, message: Message | bytes) -> dict:
        """Protobuf message -> Dict of python primitive datatypes."""
        if isinstance(message, bytes):
            proto_cls = self.get_write_proto_cls()
            # noinspection Assert
            assert proto_cls is not None, (
                f'Class {self.__class__.__name__} must provide '
                f'"Meta.proto_class" or "Meta.write_proto_class" attribute '
                f'to proses raw message'
            )
            message = proto_cls.FromString(message)
        return message_to_dict(message)

    def data_to_message(self, data: dict) -> Message:
        """Protobuf message <- Dict of python primitive datatypes."""
        """Protobuf message <- Dict of python primitive datatypes."""
        proto_cls = self.get_read_proto_cls()
        # noinspection Assert
        assert proto_cls is not None, (
            f'Class {self.__class__.__name__} must provide '
            f'"Meta.proto_class" or "Meta.read_proto_class" attribute '
            f'to generate message'
        )
        return parse_dict(data, proto_cls())

    @property
    def message(self):
        if not hasattr(self, '_message'):
            self._message = self.data_to_message(self.data)
        return self._message

    @classmethod
    def many_init(cls, *args, **kwargs):
        list_kwargs = {}
        for key in LIST_SERIALIZER_KWARGS_REMOVE:
            value = kwargs.pop(key, None)
            if value is not None:
                list_kwargs[key] = value
        list_kwargs['child'] = cls(*args, **kwargs)
        list_kwargs.update({
            key: value for key, value in kwargs.items()
            if key in LIST_SERIALIZER_KWARGS
        })
        meta = getattr(cls, 'Meta', None)
        list_serializer_class = getattr(meta, 'list_serializer_class', ListProtoSerializer)
        return list_serializer_class(*args, **list_kwargs)


class ProtoSerializer(BaseProtoSerializer, Serializer):
    pass


class ListProtoSerializer(BaseProtoSerializer, ListSerializer):
    def message_to_data(self, message):
        """
        List of protobuf messages -> List of dicts of python primitive datatypes.
        """
        if not isinstance(message, list):
            # noinspection StrFormat
            error_message = self.error_messages['not_a_list'].format(
                input_type=type(message).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [error_message]
            }, code='not_a_list')
        ret = []
        for item in message:
            ret.append(self.child.message_to_data(item))
        return ret

    def data_to_message(self, data):
        """
        List of protobuf messages <- List of dicts of python primitive datatypes.
        """
        return [
            self.child.data_to_message(item) for item in data
        ]


class ModelProtoSerializer(ProtoSerializer, ModelSerializer):
    pass