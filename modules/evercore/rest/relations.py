from __future__ import annotations
from typing import TYPE_CHECKING

from django.db.models import QuerySet, Manager
from django.utils.functional import cached_property

from rest_framework import relations

if TYPE_CHECKING:
    from typing import Callable
    from rest_framework.fields import Field


__all__ = (
    "RelatedMixin",
    "RelatedField",
    "StringRelatedField",
    "PrimaryKeyRelatedField",
    "HyperlinkedRelatedField",
    "HyperlinkedIdentityField",
    "SlugRelatedField",
)


class RelatedMixin:
    queryset: QuerySet
    parent: "Field"

    def __init__(
            self, *args,
            filter_func: str | Callable[[QuerySet], QuerySet] = None,
            **kwargs):
        self._filter = filter_func
        super().__init__(*args, **kwargs)

    @cached_property
    def filter_func(self) -> Callable[[QuerySet], QuerySet] | None:
        _filter = self._filter
        if not _filter:
            return None
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
            if _filter := self.filter_func:
                queryset = _filter(queryset)
                if queryset is None:
                    raise AssertionError(
                        f'Filter `{_filter}` must return a queryset')
            else:
                queryset = queryset.all()
        return queryset


class RelatedField(RelatedMixin, relations.RelatedField):
    pass


class StringRelatedField(RelatedMixin, relations.StringRelatedField):
    pass


class PrimaryKeyRelatedField(RelatedMixin, relations.PrimaryKeyRelatedField):
    pass


class HyperlinkedRelatedField(RelatedMixin, relations.HyperlinkedRelatedField):
    pass


class HyperlinkedIdentityField(RelatedMixin, relations.HyperlinkedIdentityField):
    pass


class SlugRelatedField(RelatedMixin, relations.SlugRelatedField):
    pass
