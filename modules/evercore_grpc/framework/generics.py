from __future__ import annotations
from typing import TYPE_CHECKING

import grpc

from django.db.models.query import QuerySet
from django.shortcuts import get_object_or_404
from django.core.exceptions import ValidationError
from django.http import Http404

from . import mixins, services

if TYPE_CHECKING:
    pass


class GenericService(services.Service):
    """
    Base class for all other generic services.
    """
    # You'll need to either set these attributes,
    # or override `get_queryset()`/`get_serializer_class()`.
    # If you are overriding a view method, it is important that you call
    # `get_queryset()` instead of accessing the `queryset` property directly,
    # as `queryset` will get evaluated only once, and those results are cached
    # for all subsequent requests.
    queryset = None
    serializer_class = None

    # If you want to use object lookups other than pk, set 'lookup_field'.
    # For more complex lookup requirements override `get_object()`.
    lookup_field = 'pk'
    lookup_request_field = None

    # The filter backend classes to use for queryset filtering
    filter_backends = ()

    # Allow generic typing checking for generic views.
    def __class_getitem__(cls, *args, **kwargs):
        return cls

    def get_queryset(self):
        """
        Get the list of items for this view.
        This must be an iterable, and may be a queryset.
        Defaults to using `self.queryset`.

        This method should always be used rather than accessing `self.queryset`
        directly, as `self.queryset` gets evaluated only once, and those results
        are cached for all subsequent requests.

        You may want to override this if you need to provide different
        querysets depending on the incoming request.

        (Eg. return a list of items that is specific to the user)
        """
        assert self.queryset is not None, (
            "'%s' should either include a `queryset` attribute, "
            "or override the `get_queryset()` method."
            % self.__class__.__name__
        )

        queryset = self.queryset
        if isinstance(queryset, QuerySet):
            # Ensure queryset is re-evaluated on each request.
            queryset = queryset.all()
        return queryset

    def get_object(self):
        """
        Returns an object instance that should be used for detail services.
        Defaults to using the lookup_field parameter to filter the base
        queryset.
        """
        queryset = self.filter_queryset(self.get_queryset())
        # lookup_field = (
        #     self.lookup_field
        #     or model_meta.get_model_pk(queryset.model).name
        # )
        lookup_request_field = self.lookup_request_field or self.lookup_field
        assert hasattr(self.request, lookup_request_field), (
            'Expected service %s to be called with request that has a field '
            'named "%s". Fix your request protocol definition, or set the '
            '`.lookup_field` attribute on the service correctly.' %
            (self.__class__.__name__, lookup_request_field)
        )
        lookup_value = getattr(self.request, lookup_request_field)
        filter_kwargs = {self.lookup_field: lookup_value}
        try:
            return get_object_or_404(queryset, **filter_kwargs)
        except (TypeError, ValueError, ValidationError, Http404):
            self.context.abort(grpc.StatusCode.NOT_FOUND, (
                '%s: %s not found!' %
                (queryset.model.__name__, lookup_value)
            ))

    def get_serializer_class(self):
        """
        Return the class to use for the serializer.
        Defaults to using `self.serializer_class`.

        You may want to override this if you need to provide different
        serializations depending on the incoming request.

        (Eg. admins get full serialization, others get basic serialization)
        """
        assert self.serializer_class is not None, (
                "'%s' should either include a `serializer_class` attribute, "
                "or override the `get_serializer_class()` method."
                % self.__class__.__name__
        )

        return self.serializer_class

    def get_serializer(self, *args, **kwargs):
        """
        Return the serializer instance that should be used for validating and
        deserializing input, and for serializing output.
        """
        serializer_class = self.get_serializer_class()
        kwargs.setdefault('context', self.get_serializer_context())
        return serializer_class(*args, **kwargs)

    def get_serializer_context(self):
        """
        Extra context provided to the serializer class.  Defaults to including
        ``grpc_request``, ``grpc_context``, and ``service`` keys.
        """
        return {
            'grpc_request': self.request,
            'grpc_context': self.context,
            'service': self,
        }

    def filter_queryset(self, queryset):
        """
        Given a queryset, filter it with whichever filter backend is in use.

        You are unlikely to want to override this method, although you may need
        to call it either from a list view, or from a custom `get_object`
        method if you want to apply the configured filtering backend to the
        default queryset.
        """
        for backend in list(self.filter_backends):
            queryset = backend().filter_queryset(self.request, queryset, self)
        return queryset


class CreateService(mixins.CreateModelMixin,
                    GenericService):
    """
    Concrete service for creating a model instance that provides a ``Create()``
    handler.
    """
    pass


class ListService(mixins.ListModelMixin,
                  GenericService):
    """
    Concrete service for listing a queryset that provides a ``List()`` handler.
    """
    pass


class RetrieveService(mixins.RetrieveModelMixin,
                      GenericService):
    """
    Concrete service for retrieving a model instance that provides a
    ``Retrieve()`` handler.
    """
    pass


class DestroyService(mixins.DestroyModelMixin,
                     GenericService):
    """
    Concrete service for deleting a model instance that provides a ``Destroy()``
    handler.
    """
    pass


class UpdateService(mixins.UpdateModelMixin,
                    GenericService):
    """
    Concrete service for updating a model instance that provides a
    ``Update()`` handler.
    """
    pass


class ReadOnlyModelService(mixins.RetrieveModelMixin,
                           mixins.ListModelMixin,
                           GenericService):
    """
    Concrete service that provides default ``List()`` and ``Retrieve()``
    handlers.
    """
    pass


class ModelService(mixins.CreateModelMixin,
                   mixins.RetrieveModelMixin,
                   mixins.UpdateModelMixin,
                   mixins.DestroyModelMixin,
                   mixins.ListModelMixin,
                   GenericService):
    """
    Concrete service that provides default ``Create()``, ``Retrieve()``,
    ``Update()``, ``Destroy()`` and ``List()`` handlers.
    """
    pass
