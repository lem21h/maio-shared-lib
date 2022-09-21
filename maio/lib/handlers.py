import re
import sre_constants
import sre_parse
from http import HTTPStatus
from json import JSONDecodeError
from time import (
    time_ns
)
from typing import (
    Any,
    Callable,
    Dict,
    Optional,
)

from aiohttp import (
    hdrs,
    web
)
from aiohttp.abc import Request
from aiohttp.web_exceptions import HTTPMethodNotAllowed
from aiohttp.web_response import Response
from aiohttp.web_urldispatcher import (
    PATH_SEP,
    Resource,
)
from yarl import URL

from maio.lib.configs.app import DomainConfig
from maio.lib.response import ErrorResponse
from maio.lib.response import UnauthorizedResponse
from maio.lib.session.service import SessionException

_MSEC_NS = 1_000_000


def to_const(value: str) -> str:
    return value.upper().replace(" ", "_")


def error_middleware(logger):
    @web.middleware
    async def _middleware(request: Request, handler):
        ts_start = time_ns()
        response = None
        try:
            response = await handler(request)

            return response

        except web.HTTPException as exception:
            message = exception.reason
            response = ErrorResponse(to_const(message), status=HTTPStatus(exception.status), details=None)
            return response

        except SessionException as exception:
            logger.warning("Session assertion failed")
            response = UnauthorizedResponse(exception.code, exception.additional)
            return response

        except (JSONDecodeError, UnicodeDecodeError):
            status = HTTPStatus.UNSUPPORTED_MEDIA_TYPE
            response = ErrorResponse("UNSUPPORTED_MEDIA_TYPE", status=status)
            return response

        except Exception as exception:
            logger.error("Error!", exc_info=exception)
            status = HTTPStatus.INTERNAL_SERVER_ERROR
            response = ErrorResponse("INTERNAL_SERVER_ERROR", status=status)
            return response

        finally:
            if response is not None:
                ts_end = time_ns()
                logger.info(f"[{request.method}] {request.raw_path} -> {response.status} [{(ts_end - ts_start) / _MSEC_NS} ms]")

    return _middleware


def resource(path: str, handler: Callable, name: str = None):
    resource = RegexResource(path, name=name)
    resource.add_route("*", handler)

    return resource


class Handler:
    __slots__ = ('__methods__',)

    def __init__(self):
        self.__methods__ = {}
        for method in hdrs.METH_ALL:
            handler = getattr(self, method.lower(), None)
            if handler:
                self.__methods__[method] = handler

    def __call__(self, request: Request):
        return self.__methods__.get(request.method, self.not_allowed)(request, **request.match_info)

    async def not_allowed(self, request: Request, **kwargs):
        raise HTTPMethodNotAllowed(request.method, self.__methods__.keys())

    async def options(self, request: Request, **kwargs):
        return Response(headers={'Access-Control-Allow-Methods': ",".join(self.__methods__.keys())})


class RegexResource(Resource):
    def __init__(self, path: str, *, name: Optional[str] = None) -> None:
        super().__init__(name=name)
        try:
            compiled = re.compile(path)
        except re.error as exc:
            raise ValueError(f"Bad pattern '{path}': {exc}") from None
        assert compiled.pattern.startswith(PATH_SEP)
        self._pattern = compiled
        self._formatter = self.reverse_regex(self._pattern)

    def reverse_regex(self, compiled: re.Pattern) -> str:
        reversed = []
        indexes_names = {value: key for key, value in compiled.groupindex.items()}

        for part in sre_parse.parse(compiled.pattern):
            code, data = part
            if code == sre_constants.SUBPATTERN:
                index, *_ = data
                reversed.append(f"{{{indexes_names[index]}}}")
            elif code == sre_constants.LITERAL:
                reversed.append(chr(data))
        return "".join(reversed)

    @property
    def canonical(self) -> str:
        return self._formatter

    def add_prefix(self, prefix: str) -> None:
        assert prefix.startswith('/')
        assert not prefix.endswith('/')
        assert len(prefix) > 1
        self._pattern = re.compile(re.escape(prefix) + self._pattern.pattern)
        self._formatter = prefix + self._formatter

    def _match(self, path: str) -> Optional[Dict[str, str]]:
        match = self._pattern.fullmatch(path)
        if match is None:
            return None
        else:
            return {key: URL.build(path=value, encoded=True).path
                    for key, value in match.groupdict().items()}

    def raw_match(self, path: str) -> bool:
        return self._formatter == path

    def get_info(self) -> Dict[str, Any]:
        return {'formatter': self._formatter,
                'pattern': self._pattern}

    def url_for(self, **parts: str) -> URL:
        url = self._formatter.format_map({k: URL.build(path=v).raw_path
                                          for k, v in parts.items()})
        return URL.build(path=url)

    def __repr__(self) -> str:
        name = f"'{self.name}' " if self.name is not None else ""
        return "<Regex {name} {formatter}>".format(name=name, formatter=self._formatter)


class HeadersHandler:
    __slots__ = ('config', 'server_name', 'allowed_headers')

    def __init__(self, domain_config: DomainConfig, server_name: str):
        self.config = domain_config
        self.server_name = server_name
        self.allowed_headers = ','.join(domain_config.headers)

    async def handle(self, request: Request, response):
        domain_config = self.config

        origin = request.headers.getone('Origin', None)

        if origin not in domain_config.origins:
            origin = next(iter(domain_config.origins))

        response.headers.add('Access-Control-Allow-Credentials', 'true')
        response.headers.add('Access-Control-Allow-Origin', origin)
        response.headers.add('Access-Control-Allow-Headers', self.allowed_headers)
        response.headers['Server'] = self.server_name
