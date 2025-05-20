from msgpack import packb, unpackb


__all__ = ("pack_data", "unpack_data")


def pack_data(o, **kwargs):
    kwargs["use_bin_type"] = True
    kwargs["datetime"] = True
    return packb(o, **kwargs)


def unpack_data(o, **kwargs):
    kwargs["raw"] = False
    kwargs["timestamp"] = 3
    return unpackb(o, **kwargs)


def register_msgpack():
    from kombu.serialization import register

    register(
        'msgpack', pack_data, unpack_data,
        content_type='application/x-msgpack',
        content_encoding='binary')


register_msgpack()
