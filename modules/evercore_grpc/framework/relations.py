from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import QuerySet, Manager
from django.utils.functional import cached_property

from rest_framework import relations
from rest_framework.fields import empty

from .fields import ProtoFieldMixin, ProtoIterableFieldMixin

if TYPE_CHECKING:
    from typing import Callable


__all__ = (
    "RelatedField",
    "StringRelatedField", "PrimaryKeyRelatedField", "HyperlinkedRelatedField",
    "HyperlinkedIdentityField", "SlugRelatedField", "ManyRelatedField",
)


class ProtoRelationFieldMixin(ProtoFieldMixin):
    def decide_null(self, value):
        if value in ['', 0]:
            if not self.required:
                return empty
            return None
        return value


class RelatedField(ProtoRelationFieldMixin, relations.RelatedField):
    def __init__(
            self, *,
            filter_func: str | Callable[[QuerySet], QuerySet] = None,
            **kwargs):
        super().__init__(**kwargs)
        self._filter = filter_func

    @cached_property
    def filter_func(self) -> Callable[[QuerySet], QuerySet]:
        _filter = self._filter
        if _filter is None:
            return lambda queryset: queryset.all()
        if callable(_filter):
            return _filter

        parent = self.parent
        while parent is not None:
            try:
                f = getattr(parent, _filter)
            except AttributeError:
                parent = parent.parent
            else:
                if not callable(f):
                    parent = parent.__class__
                    raise AssertionError(
                        f"filter_func is not callable. "
                        f"Found in `{parent.__module__}.{parent.__name__}.{_filter}`"
                    )
                return f
        raise AssertionError(f"Couldn't find filter_func `{_filter}`")

    def get_queryset(self):
        queryset = self.queryset
        if isinstance(queryset, (QuerySet, Manager)):
            _filter = self.filter_func
            queryset = _filter(queryset)
            if queryset is None:
                raise AssertionError(
                    f'Filter `{_filter}` must return a queryset')
        return queryset

    @classmethod
    def many_init(cls, *args, **kwargs):
        """
        This method handles creating a parent `ManyRelatedField` instance
        when the `many=True` keyword argument is passed.

        Typically, you won't need to override this method.

        Note that we're over-cautious in passing most arguments to both parent
        and child classes in order to try to cover the general case. If you're
        overriding this method you'll probably want something much simpler, eg:

        @classmethod
        def many_init(cls, *args, **kwargs):
            kwargs['child'] = cls()
            return CustomManyRelatedField(*args, **kwargs)
        """
        list_kwargs = {'child_relation': cls(*args, **kwargs)}
        for key in kwargs:
            if key in relations.MANY_RELATION_KWARGS:
                list_kwargs[key] = kwargs[key]
        return ManyRelatedField(**list_kwargs)


class StringRelatedField(ProtoRelationFieldMixin, relations.StringRelatedField):
    pass


class PrimaryKeyRelatedField(ProtoRelationFieldMixin, relations.PrimaryKeyRelatedField):
    pass


class HyperlinkedRelatedField(ProtoRelationFieldMixin, relations.HyperlinkedRelatedField):
    pass


class HyperlinkedIdentityField(ProtoRelationFieldMixin, relations.HyperlinkedIdentityField):
    pass


class SlugRelatedField(ProtoRelationFieldMixin, relations.SlugRelatedField):
    pass


class ManyRelatedField(ProtoIterableFieldMixin, relations.ManyRelatedField):
    pass
