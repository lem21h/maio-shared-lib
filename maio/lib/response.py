import json
from functools import singledispatch
from http import HTTPStatus
from typing import (
    Any,
    Optional,
    Union
)

from aiohttp.typedefs import LooseHeaders
from aiohttp.web_response import Response

from maio.lib.exceptions import (
    CommandException,
    Error,
    ValidationException
)
from maio.lib.session.service import SessionException


@singledispatch
def json_serializer(value):
    return str(value)


class JsonResponse(Response):
    __slots__ = ()

    def __init__(self,
                 data: Any,
                 status: HTTPStatus,
                 reason: Optional[str] = None,
                 headers: LooseHeaders = None):
        text = json.dumps(data, default=json_serializer)

        super().__init__(text=text, status=status.value, reason=reason, headers=headers, content_type='application/json')


class ErrorResponse(JsonResponse):
    def __init__(self, code: str, status: HTTPStatus, details: Optional[dict] = None):
        data = {
            'status': "ERROR",
            'code': code
        }

        if details:
            data['errors'] = details

        super().__init__(data, status=status)


class CreatedResponse(JsonResponse):
    def __init__(self, data: dict = None):
        if not data:
            data = {}

        data.update({
            "status": "OK"
        })
        super().__init__(data, status=HTTPStatus.CREATED)


class AcceptedResponse(JsonResponse):
    def __init__(self, data: dict = None):
        if not data:
            data = {}

        data.update({
            "status": "OK"
        })

        super().__init__(data, status=HTTPStatus.ACCEPTED)


class OkResponse(JsonResponse):
    __slots__ = ()

    def __init__(self, data: dict = None):
        if not data:
            data = {}

        data.update({
            "status": "OK"
        })
        super().__init__(data, status=HTTPStatus.OK)


class NotFoundResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.NOT_FOUND, details)

    @classmethod
    def from_exception(cls, exception: CommandException):
        return cls(exception.code, exception.additional)


class UnauthorizedResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.UNAUTHORIZED, details)

    @classmethod
    def from_exception(cls, exception: CommandException):
        return cls(exception.code, exception.additional)


class BadRequestResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.BAD_REQUEST, details)

    @classmethod
    def from_validation_exception(cls, validation_exception: ValidationException):

        details = {}
        if validation_exception.parameters:
            for field, error in validation_exception.parameters.items():
                if isinstance(error, Error):
                    details[field] = error.to_dict()
                else:
                    details[field] = error

        return cls(validation_exception.code, details)


class ForbiddenResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.FORBIDDEN, details)

    @classmethod
    def from_exception(cls, exception: Union[CommandException, SessionException]):
        return cls(exception.code, exception.additional)


class UnprocessableEntityResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.UNPROCESSABLE_ENTITY, details)

    @classmethod
    def from_exception(cls, exception: CommandException):
        return cls(exception.code, exception.additional)


class ConflictResponse(ErrorResponse):
    def __init__(self, code: str, details: dict = None):
        super().__init__(code, HTTPStatus.CONFLICT, details)

    @classmethod
    def from_exception(cls, exception: CommandException):
        return cls(exception.code, exception.additional)
