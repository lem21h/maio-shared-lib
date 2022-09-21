from collections.abc import MappingView
from datetime import datetime
from functools import singledispatch


@singledispatch
def json_serializer(value):
    return str(value)


@json_serializer.register(int)
def json_serializer_int(value: int):
    return value


@json_serializer.register(MappingView)
def json_serializer_mapping(value: MappingView):
    return list(value)


@json_serializer.register(set)
def json_serializer_set(value: set):
    return list(value)


@json_serializer.register(datetime)
def json_serializer_datetime(value: datetime):
    return value.strftime('%Y-%m-%dT%H:%M:%SZ')
