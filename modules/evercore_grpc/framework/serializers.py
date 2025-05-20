from __future__ import annotations
from typing import TYPE_CHECKING

from collections.abc import Mapping

from google.protobuf.message import Message

from django.contrib.postgres import fields as postgres_fields
from django.core.exceptions import ValidationError as DjangoValidationError
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _

from rest_framework import serializers
from rest_framework.exceptions import ValidationError
# Non-field imports, but public API
from rest_framework.fields import (
    CreateOnlyDefault, CurrentUserDefault, SkipField, empty, HiddenField, get_error_detail
)
from rest_framework.relations import Hyperlink, PKOnlyObject
from rest_framework.utils.field_mapping import get_nested_relation_kwargs

from evercore_grpc.protobuf.json_format import parse_dict
from evercore_grpc.settings import api_settings

from .fields import (
    ProtoFieldMixin,
    BooleanField, CharField, ChoiceField, DateField, DateTimeField, DecimalField,
    DictField, DurationField, EmailField, Field, FileField, FilePathField, FloatField,
    HStoreField, IPAddressField, ImageField, IntegerField, JSONField, ListField,
    ModelField, MultipleChoiceField, ReadOnlyField, RegexField, SerializerMethodField,
    SlugField, TimeField, URLField, UUIDField,
    BinaryField, PhoneNumberField, OneOfField,
)
from .relations import (
    HyperlinkedIdentityField, HyperlinkedRelatedField, ManyRelatedField,
    PrimaryKeyRelatedField, RelatedField, SlugRelatedField, StringRelatedField,
)


if TYPE_CHECKING:
    type InitialDataTypes = dict | Message | bytes | list

    from typing import Callable, Any, Generator
    from rest_framework.utils.serializer_helpers import BindingDict
    from .fields import Field


class BaseProtoSerializerMixin(ProtoFieldMixin):
    initial_data: "InitialDataTypes"
    allow_null: bool
    run_validation: "Callable[[InitialDataTypes | empty], Any]"
    _validated_data: dict
    validated_data: dict
    _errors: dict
    errors: dict
    _data: dict
    data: dict
    _message: Message

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

    def bytes_to_message(self, value: bytes) -> Message:
        proto_cls = self.write_proto_cls
        # noinspection Assert
        assert proto_cls is not None, (
            f'Class {self.__class__.__name__} must provide '
            f'"Meta.write_proto_class" or "Meta.proto_class" attribute '
            f'to convert raw message')
        return proto_cls.FromString(value)

    def data_to_message(self, data: dict) -> Message:
        proto_cls = self.read_proto_cls
        # noinspection Assert
        assert proto_cls is not None, (
            f'Class {self.__class__.__name__} must provide '
            f'"Meta.read_proto_class" or "Meta.proto_class" attribute '
            f'to generate message object'
        )
        return parse_dict(data, proto_cls())

    def convert_initial_data(self):
        data = self.initial_data
        if isinstance(data, bytes):
            return self.bytes_to_message(data)
        return data

    def is_valid(self, *, raise_exception=False):
        if not hasattr(self, 'initial_data'):
            message = (
                'Cannot call `.is_valid()` as no `data=` keyword argument was '
                'passed when instantiating the serializer instance.'
            )
            raise AssertionError(message)

        if not hasattr(self, '_validated_data'):
            try:
                self.initial_data = self.convert_initial_data()
                self._validated_data = self.run_validation(self.initial_data)
            except serializers.ValidationError as exc:
                self._validated_data = {}
                self._errors = exc.detail
            else:
                self._errors = {}

        if self._errors and raise_exception:
            raise ValidationError(self.errors)

        return not bool(self._errors)

    @property
    def message(self) -> Message:
        if not hasattr(self, "_message"):
            self._message = self.data_to_message(self.data)
        return self._message


class BaseSerializer(BaseProtoSerializerMixin, serializers.BaseSerializer):
    pass


class ProtoSerializerMixin(BaseProtoSerializerMixin):
    fields: BindingDict
    _writable_fields: "Generator[Field]"

    def get_initial(self):
        if hasattr(self, 'initial_data'):
            self.initial_data = self.convert_initial_data()
            # initial_data may not be a valid type
            if not isinstance(self.initial_data, (Mapping, Message)):
                return {}

            return {
                field_name: field.get_value(self.initial_data)
                for field_name, field in self.fields.items()
                if (field.get_value(self.initial_data) is not empty) and
                not field.read_only
            }

        return {
            field.field_name: field.get_initial()
            for field in self.fields.values()
            if not field.read_only
        }

    def to_internal_value(self, data):
        """
        Dict of native values <- Dict of primitive datatypes.
        """
        if not isinstance(data, (Mapping, Message)):
            message = self.error_messages['invalid'].format(
                datatype=type(data).__name__
            )
            raise ValidationError({
                api_settings.NON_FIELD_ERRORS_KEY: [message]
            }, code='invalid')

        ret = {}
        errors = {}
        fields = self._writable_fields

        for field in fields:
            validate_method = getattr(self, 'validate_' + field.field_name, None)
            primitive_value = field.get_value(data)
            try:
                validated_value = field.run_validation(primitive_value)
                if validate_method is not None:
                    validated_value = validate_method(validated_value)
            except ValidationError as exc:
                errors[field.field_name] = exc.detail
            except DjangoValidationError as exc:
                errors[field.field_name] = get_error_detail(exc)
            except SkipField:
                pass
            else:
                self.set_value(ret, field.source_attrs, validated_value)

        if errors:
            raise ValidationError(errors)

        return ret


class Serializer(ProtoSerializerMixin, serializers.Serializer):
    default_error_messages = {
        'invalid': _('Invalid data. Expected a dictionary or Message, but got {datatype}.')
    }


class ListSerializerMixin(BaseProtoSerializerMixin, serializers.ListSerializer):
    def get_initial(self):
        if hasattr(self, 'initial_data'):
            data = self.initial_data
            if not isinstance(data, list) or not data:
                return []

            def _iterate_data() -> Generator:
                for item in data:
                    if isinstance(item, bytes):
                        yield self.child.bytes_to_message(item)
                    else:
                        yield item

            def _iterate_value() -> Generator[dict]:
                fields = (
                    (field_name, field)
                    for field_name, field in self.child.fields.items()
                    if not field.read_only
                )

                for item in _iterate_data():
                    ret = {}
                    for field_name, field in fields:
                        if (value := field.get_value(item)) is not empty:
                            ret[field_name] = value
                    yield ret

            return list(_iterate_value())
        return []

    def run_child_validation(self, data):
        """
        Run validation on child serializer.
        You may need to override this method to support multiple updates. For example:

        self.child.instance = self.instance.get(pk=data['id'])
        self.child.initial_data = data
        return super().run_child_validation(data)
        """
        if isinstance(data, bytes):
            data = self.child.bytes_to_message(data)
        return self.child.run_validation(data)


class ModelSerializer(ProtoSerializerMixin, serializers.ModelSerializer):
    serializer_field_mapping = {
        models.AutoField: IntegerField,
        models.BigIntegerField: IntegerField,
        models.BooleanField: BooleanField,
        models.CharField: CharField,
        models.CommaSeparatedIntegerField: CharField,
        models.DateField: DateField,
        models.DateTimeField: DateTimeField,
        models.DecimalField: DecimalField,
        models.DurationField: DurationField,
        models.EmailField: EmailField,
        models.Field: ModelField,
        models.FileField: FileField,
        models.FloatField: FloatField,
        models.ImageField: ImageField,
        models.IntegerField: IntegerField,
        models.NullBooleanField: BooleanField,
        models.PositiveIntegerField: IntegerField,
        models.PositiveSmallIntegerField: IntegerField,
        models.SlugField: SlugField,
        models.SmallIntegerField: IntegerField,
        models.TextField: CharField,
        models.TimeField: TimeField,
        models.URLField: URLField,
        models.UUIDField: UUIDField,
        models.GenericIPAddressField: IPAddressField,
        models.FilePathField: FilePathField,
        models.BinaryField: BinaryField,
    }
    if hasattr(models, 'JSONField'):
        serializer_field_mapping[models.JSONField] = JSONField
    if postgres_fields:
        serializer_field_mapping[postgres_fields.HStoreField] = HStoreField
        serializer_field_mapping[postgres_fields.ArrayField] = ListField
        serializer_field_mapping[postgres_fields.JSONField] = JSONField
    serializer_related_field = PrimaryKeyRelatedField
    serializer_related_to_field = SlugRelatedField
    serializer_url_field = HyperlinkedIdentityField
    serializer_choice_field = ChoiceField

    default_error_messages = {
        'invalid': _('Invalid data. Expected a dictionary or Message, but got {datatype}.')
    }


class HyperlinkedModelSerializer(ModelSerializer):
    """
    A type of `ModelSerializer` that uses hyperlinked relationships instead
    of primary key relationships. Specifically:

    * A 'url' field is included instead of the 'id' field.
    * Relationships to other instances are hyperlinks, instead of primary keys.
    """
    serializer_related_field = HyperlinkedRelatedField

    def get_default_field_names(self, declared_fields, model_info):
        """
        Return the default list of field names that will be used if the
        `Meta.fields` option is not specified.
        """
        return (
            [self.url_field_name] +
            list(declared_fields) +
            list(model_info.fields) +
            list(model_info.forward_relations)
        )

    def build_nested_field(self, field_name, relation_info, nested_depth):
        """
        Create nested fields for forward and reverse relationships.
        """
        class NestedSerializer(HyperlinkedModelSerializer):
            class Meta:
                model = relation_info.related_model
                depth = nested_depth - 1
                fields = '__all__'

        field_class = NestedSerializer
        field_kwargs = get_nested_relation_kwargs(relation_info)

        return field_class, field_kwargs
