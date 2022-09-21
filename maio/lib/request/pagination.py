from typing import (
    NamedTuple,
    Type
)


class Direction:
    __slots__ = ()


class AscDirection(Direction):
    __slots__ = ()

    @staticmethod
    def opposite() -> Type[Direction]:
        return DescDirection


class DescDirection(Direction):
    __slots__ = ()

    @staticmethod
    def opposite() -> Type[Direction]:
        return AscDirection


class Sort(NamedTuple):
    field: str
    direction: Type[Direction]

    @classmethod
    def asc(cls, field: str):
        return cls(field, AscDirection)

    @classmethod
    def desc(cls, field: str):
        return cls(field, DescDirection)


class Pagination(NamedTuple):
    limit: int
    offset: int

    def need_count(self, count):
        return count == self.limit or (self.limit < self.offset and count == 0)
