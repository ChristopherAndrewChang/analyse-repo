from __future__ import annotations
from typing import TYPE_CHECKING

from django.db import models
from django.utils.translation import gettext_lazy as _

from evercore.constants import GLOBAL_ID_LENGTH

from idvalid_core.generators import default_subid_generator

if TYPE_CHECKING:
    from typing import Callable
    from datetime import datetime


    class SubIDModelProtocol(models.Model):
        subid: str

        class Meta:
            abstract = True


    class AccessLogModelProtocol[T](models.Model):
        created: datetime | None
        created_by: T | None
        modified: datetime | None
        modified_by: T | None
        is_deleted: bool
        deleted: datetime | None
        deleted_by: T | None

        class Meta:
            abstract = True


# noinspection PyUnusedLocal
def default_class_getitem(cls, *args, **kwargs):
    return cls


def get_subid_model(
        *,
        max_length: int = GLOBAL_ID_LENGTH,
        default: Callable[[], str] = default_subid_generator
) -> type[SubIDModelProtocol]:
    """
    Generate a Django model class with a `subid` field.

    This function dynamically creates and returns a Django model class with a `subid` field,
    which is a `CharField` with a specified maximum length and default value. The created
    model class inherits from `models.Model` and is abstract.

    Parameters
    ----------
    max_length : int, optional
        The maximum length of the `subid` field. Defaults to 64.
    default : Callable[[], str], optional
        A callable that returns the default value for the `subid` field. Defaults to
        `default_subid_generator`.

    Returns
    -------
    type[SubIDModelProtocol]
        A dynamically created Django model class with a `subid` field.

    Notes
    -----
    - The `subid` field is defined as a `CharField` with the following attributes:
        - `max_length`: Set to the value of `max_length` parameter.
        - `db_column`: Set to "subid".
        - `unique`: Set to `True`.
        - `null`: Set to `True`.
        - `blank`: Set to `True`.
        - `editable`: Set to `False`.
        - `default`: Set to the callable passed as `default` parameter.
        - `help_text`: Describes the purpose of the field as "Primary key shown to user."

    - The generated model class is abstract and cannot be instantiated directly.
    - The `__class_getitem__` method is set to `default_class_getitem`.
    """
    return type['SubIDModelProtocol'](
        "SubIDModel", (models.Model,), {
            "__module__": __name__,
            "__qualname__": "SubIDModel",
            "__class_getitem__": default_class_getitem,
            "subid": models.CharField(
                _("subid"),
                max_length=max_length,
                db_column="subid",
                unique=True,
                null=True,
                blank=True,
                editable=False,
                default=default,
                help_text=_("Primary key shown to user.")),
            "Meta": type(
                "Meta", (), {
                    "abstract": True
                }
            )
        }
    )


def get_access_log_model(
        user_model: str | type(models.Model)) -> type[AccessLogModelProtocol]:
    """
    Generate an abstract Django model for access logging.

    This function dynamically creates a Django model class that includes
    fields for logging creation, modification, and deletion activities.
    It provides an abstract base model for tracking changes and deletions,
    with the user model specified for the `ForeignKey` relationships.

    Parameters
    ----------
    user_model : str | models.Model
        A string representing the name of the user model or a Django model class.
        This model is used for the `ForeignKey` fields to link to the users who
        created, modified, or deleted the instance.

    Returns
    -------
    type[AccessLogModelProtocol]
        A dynamically created Django model class that adheres to the
        `AccessLogModelProtocol` interface. This class includes fields for
        creation, modification, deletion timestamps, and associated user
        references.

    Notes
    -----
    The dynamically created model includes the following fields:
    - `created`: Timestamp of when the instance was created.
    - `created_by`: ForeignKey to the user who created the instance.
    - `modified`: Timestamp of the last modification.
    - `modified_by`: ForeignKey to the user who last modified the instance.
    - `is_deleted`: Boolean indicating whether the instance is deleted.
    - `deleted`: Timestamp of when the instance was deleted.
    - `deleted_by`: ForeignKey to the user who deleted the instance.

    The model is created with the `Meta` class set to `abstract`,
    so it cannot be instantiated directly but serves as a base class
    for other models.

    Examples
    --------
    >>> from django.db import models
    >>> from django.contrib.auth.models import User
    >>> AccessLogModel = get_access_log_model(User)
    >>> class MyModel(AccessLogModel):
    >>>     name = models.CharField(max_length=255)
    >>>     # Additional fields and methods for MyModel

    """
    return type['AccessLogModelProtocol'](
        "AccessLogModel", (models.Model,), {
            "__module__": __name__,
            "__qualname__": "AccessLogModel",
            "__class_getitem__": default_class_getitem,
            "created": models.DateTimeField(
                _('created'),
                auto_now_add=True,
                null=True,
                blank=True,
                editable=False),
            "created_by": models.ForeignKey(
                user_model,
                on_delete=models.CASCADE,
                related_name="%(app_label)s_%(class)ss_created_by",
                db_index=False,
                verbose_name=_('created by'),
                null=True,
                blank=True,
                editable=False),
            "modified": models.DateTimeField(
                _('modified'),
                auto_now=True,
                null=True,
                blank=True,
                editable=False),
            "modified_by": models.ForeignKey(
                user_model,
                on_delete=models.CASCADE,
                related_name="%(app_label)s_%(class)ss_modified_by",
                db_index=False,
                verbose_name=_('modified by'),
                null=True,
                blank=True,
                editable=False),
            "is_deleted": models.BooleanField(
                _('deleted status'),
                default=False,
                db_index=True),
            "deleted": models.DateTimeField(
                _('deleted'),
                null=True,
                blank=True,
                editable=False),
            "deleted_by": models.ForeignKey(
                user_model,
                on_delete=models.CASCADE,
                related_name="%(app_label)s_%(class)ss_deleted_by",
                db_index=False,
                verbose_name=_('deleted by'),
                null=True,
                blank=True,
                editable=False),
            "Meta": type(
                "Meta", (), {
                    "abstract": True
                }
            )
        }
    )
