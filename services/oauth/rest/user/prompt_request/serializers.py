from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from django.utils.translation import gettext_lazy as _

from rest_framework import serializers

from oauth.models import PromptRequest

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = (
    "AnswerSerializer",
)


class AnswerSerializer(serializers.Serializer):
    answer = serializers.ChoiceField(
        choices=PromptRequest.ANSWER_CHOICES)

    def update(
            self, instance: PromptRequest,
            validated_data: dict) -> PromptRequest:
        instance.set_answer(validated_data["answer"])
        return instance
