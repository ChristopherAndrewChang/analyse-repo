from __future__ import annotations
from typing import TYPE_CHECKING

import logging

from evercore_grpc.framework import serializers

from idvalid_integration.protos.cryptography.asymmetric.key_pb2 import Algorithm

if TYPE_CHECKING:
    pass


logger = logging.getLogger(__name__)
__all__ = ("PairSerializer", "GenerateKeySerializer")


class PairSerializer(serializers.Serializer):
    private_key = serializers.BinaryField()
    public_key = serializers.BinaryField()


class GenerateKeySerializer(serializers.Serializer):
    data = serializers.BinaryField(write_only=True)
    algorithm = serializers.ChoiceField(
        choices=tuple(zip(Algorithm.values(), Algorithm.keys())),
        write_only=True)
    signature = serializers.BinaryField(read_only=True)
    pair = PairSerializer(read_only=True)

    def create(self, validated_data):
        raise Exception(validated_data)
