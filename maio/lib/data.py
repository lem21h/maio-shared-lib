from enum import IntEnum
from typing import Set


class LabelEnum(IntEnum):
    __slots__ = ()

    @classmethod
    def _build_map(cls):
        cls._A = {value.name: value for value in cls}

    @classmethod
    def get_labels(cls) -> Set[str]:
        try:
            return set(cls._A.keys())
        except AttributeError:
            cls._build_map()
        return set(cls._A.keys())

    @classmethod
    def from_label(cls, label: str) -> 'LabelEnum':
        try:
            cls._A[label]
        except AttributeError:
            cls._build_map()

        return cls._A[label]
