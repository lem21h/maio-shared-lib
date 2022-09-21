from typing import (
    Any,
    Dict,
    Optional
)


class Error:
    __slots__ = ('code', 'parameters')
    code: str
    parameters: Optional[dict]

    def __init__(self, code: str, parameters: Optional[Dict]):
        self.code = code
        self.parameters = parameters

    @classmethod
    def new(cls, code: str):
        return cls(code, None)

    def to_dict(self):
        return {"code": self.code} if not self.parameters else {"code": self.code, "parameters": self.parameters}

    def __repr__(self):
        return f'ERROR({self.code})'


INVALID_OBJECT = Error("INVALID_KIND", {"expected": "object"})
INVALID_ARRAY = Error("INVALID_KIND", {"expected": "array"})
INVALID_STRING = Error("INVALID_KIND", {"expected": "string"})
INVALID_UUID = Error("INVALID_KIND", {"expected": "UUID"})
INVALID_DATE = Error("INVALID_KIND", {"expected": "date"})
INVALID_DATETIME = Error("INVALID_KIND", {"expected": "datetime"})
INVALID_BOOL = Error("INVALID_KIND", {"expected": "bool"})
INVALID_EMAIL = Error("INVALID_KIND", {"expected": "email"})
INVALID_PHONE = Error("INVALID_KIND", {"expected": "phone"})
INVALID_NUMBER = Error("INVALID_KIND", {"expected": "number"})
INVALID_FIXED_FLOAT = Error("INVALID_KIND", {"expected": "fixedFloat"})

ERROR_MISSING = Error.new("MISSING")


def too_small(min_value: Any) -> Error:
    return Error("TOO_SMALL", {"required": min_value})


def too_big(max_value: Any) -> Error:
    return Error("TOO_BIG", {"required": max_value})
