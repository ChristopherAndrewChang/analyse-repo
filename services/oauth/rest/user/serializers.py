from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "AllowSerializer",
)


class AllowSerializer(serializers.Serializer):
    client_id = serializers.CharField()
    redirect_uri = serializers.URLField()

    scope = serializers.CharField(default=None)

    response_type = serializers.CharField(required=False)
    state = serializers.CharField(required=False)
    code_challenge = serializers.CharField(required=False)
    code_challenge_method = serializers.CharField(required=False)
    nonce = serializers.CharField(required=False)
    claims = serializers.CharField(required=False)
