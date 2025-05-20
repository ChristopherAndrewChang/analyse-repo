from django.test import TestCase

# Create your tests here.

from evercore_grpc.framework import serializers
from google.protobuf.wrappers_pb2 import BoolValue

class TestSerializer(serializers.Serializer):
    boolean_field = serializers.BooleanField()
    char_field = serializers.CharField()
    email_field = serializers.EmailField()
    regex_field = serializers.RegexField(r'^[\d-]+$')
    slug_field = serializers.SlugField()
    url_field = serializers.URLField()
    uuid_field = serializers.UUIDField()
    ipaddress_field = serializers.IPAddressField()

    integer_field = serializers.IntegerField()
    float_field = serializers.FloatField()
    decimal_field = serializers.DecimalField(
        max_digits=10, decimal_places=5)

    datetime_field = serializers.DateTimeField()
    # date_field = serializers.DateField()
    # time_field = serializers.TimeField()
    duration_field = serializers.DurationField()

    choice_field = serializers.ChoiceField(
        choices=(
            (1, "first"),
            (2, "second"),
            (3, "third"),
        ))
    multiple_choice_field = serializers.MultipleChoiceField(
        choices=(
            (1, "first"),
            (2, "second"),
            (3, "third"),
        ))

    list_field = serializers.ListField()
    dict_field = serializers.DictField()


