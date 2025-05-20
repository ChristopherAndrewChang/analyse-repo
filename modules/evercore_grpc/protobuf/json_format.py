from google.protobuf.json_format import MessageToDict, ParseDict


__all__ = ("message_to_dict", "parse_dict")


def message_to_dict(message, **kwargs):
    kwargs.setdefault('always_print_fields_with_no_presence', False)
    kwargs.setdefault('preserving_proto_field_name', True)
    kwargs.setdefault('use_integers_for_enums', True)
    return MessageToDict(message, **kwargs)


def parse_dict(js_dict, message, **kwargs):
    kwargs.setdefault('ignore_unknown_fields', True)
    return ParseDict(js_dict, message, **kwargs)
