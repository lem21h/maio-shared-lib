from typing import (
    Dict,
    Optional
)

from maio.lib.errors import Error


class CommandException(Exception):
    __slots__ = ("code", "additional")
    code: str
    additional: Optional[Dict]

    def __init__(self, code: str, additional: Optional[Dict] = None):
        self.code = code
        self.additional = additional

    def __str__(self):
        return f"{self.__class__.__name__}[code={self.code}, additional={self.additional}]"


class ValidationException(Exception):
    __slots__ = ('parameters', 'code')

    def __init__(self, parameters: Optional[dict] = None, code: str = None):
        self.parameters = parameters
        self.code = f"VALIDATION.{code}" if code else "VALIDATION.ERROR"

    @classmethod
    def single(cls, field, error):
        return cls(parameters={field: error})

    @classmethod
    def general(cls, error: Error):
        return cls(code=error.code, parameters=error.parameters)

    def extract(self, prefix: str = "", errors=None):
        if errors is None:
            errors = {}

        if prefix:
            prefix = f"{prefix}."

        for field, error in self.parameters.items():
            errors[f"{prefix}{field}"] = error

        return errors

    def extract_indexed(self, index: int, errors=None):
        return self.extract(f'[{index}]', errors)


class FatalException(Exception):
    __slots__ = ()
