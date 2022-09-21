from functools import singledispatch
from uuid import UUID


@singledispatch
def to_uuid(value):
    raise ValueError(f"{value} is not UUID")


@to_uuid.register(UUID)
def to_uuid_uuid(value):
    return value


@to_uuid.register(str)
def to_uuid_str(value):
    return UUID(value)


@to_uuid.register(bytes)
def to_uuid_bytes(value):
    return UUID(value.decode("utf-8"))
