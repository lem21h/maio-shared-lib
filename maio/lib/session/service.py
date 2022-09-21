import logging
from contextlib import asynccontextmanager
from datetime import (
    datetime,
    timedelta
)
from typing import Optional
from uuid import UUID

from aiohttp.web_request import Request
from aiohttp.web_response import Response

from maio.lib.parsers import parse_uuid
from maio.lib.session.config import SessionConfig
from maio.lib.session.model import Session
from maio.lib.session.repository import SessionMongoRepository

logger = logging.getLogger('session')


class SessionException(Exception):
    __slots__ = ('code', 'additional')

    def __init__(self, code: str, additional: Optional[dict] = None):
        self.code = f"SESSION.{code}"
        self.additional = additional


class SessionNotFoundException(SessionException):
    __slots__ = ('session_id',)

    def __init__(self, session_id: UUID):
        super().__init__("NOT_FOUND", {"sessionId": session_id})


class SessionNotExistsException(SessionException):
    __slots__ = ()

    def __init__(self):
        super().__init__("NOT_FOUND")


class SessionTokenNotFoundException(SessionException):
    __slots__ = ()

    def __init__(self):
        super().__init__("TOKEN_MISSING")


class SessionUserInactiveException(SessionException):
    __slots__ = ()

    def __init__(self):
        super().__init__("USER_INACTIVE")


class SessionInvalidTokenException(SessionException):
    __slots__ = ('expected', 'actual')

    def __init__(self, expected, actual):
        super().__init__("TOKEN_INVALID")
        self.expected = expected
        self.actual = actual


class SessionStore:
    __slots__ = ()

    def get_by_id(self, request: Request) -> Optional[str]:
        raise NotImplementedError

    def add_to_response(self, response: Response, session: Session):
        raise NotImplementedError

    def remove_from_response(self, response: Response):
        raise NotImplementedError


class CookieSessionStore(SessionStore):
    __slots__ = ('session_config', 'cookie_name')

    def __init__(self,
                 session_config: SessionConfig,
                 suffix: str):
        self.session_config = session_config
        self.cookie_name = f'{session_config.cookie_name}_{suffix}'

    def get_by_id(self, request: Request) -> Optional[str]:
        session_id = request.cookies.get(self.cookie_name, None)

        return session_id

    def add_to_response(self, response: Response, session: Session):
        # noinspection PyTypeChecker
        response.set_cookie(self.cookie_name,
                            str(session.id),
                            max_age=86400,
                            secure=self.session_config.cookie_secure,
                            httponly=self.session_config.cookie_secure,
                            samesite=self.session_config.cookie_samesite)

    def remove_from_response(self, response: Response):
        response.del_cookie(self.cookie_name)


class HeaderSessionStore(SessionStore):
    __slots__ = ('session_config', 'header_name')

    def __init__(self,
                 session_config: SessionConfig,
                 suffix: str):
        self.session_config = session_config
        self.header_name = f'X-Session-{suffix.title()}'

    def get_by_id(self, request: Request) -> Optional[str]:
        session_id = request.headers.getone(self.header_name, None)

        return session_id

    def add_to_response(self, response: Response, session: Session):
        response.headers.add(self.header_name, str(session.id))

    def remove_from_response(self, response: Response):
        # noinspection PyBroadException
        try:
            response.headers.popall(self.header_name)
        except:
            pass


class SessionManager:
    __slots__ = ('client_store', 'repository', 'session_validity')

    repository: SessionMongoRepository
    config: SessionConfig
    name: str

    def __init__(self,
                 session_config: SessionConfig,
                 sessions_repository: SessionMongoRepository,
                 store: SessionStore):
        super().__init__()
        self.session_validity = timedelta(seconds=session_config.session_valid)
        self.client_store = store
        self.repository = sessions_repository

    @asynccontextmanager
    async def session(self, request: Request):
        session_id = self.client_store.get_by_id(request)

        if not session_id:
            raise SessionNotExistsException

        session_id = parse_uuid(session_id)

        if not session_id:
            raise SessionNotExistsException

        valid_till = self.get_validity()
        session = await self.repository.update_active_valid_till_by_id(valid_till, session_id)

        if not session:
            raise SessionNotFoundException(session_id)

        if not session.active:
            raise SessionUserInactiveException

        try:
            yield session
        finally:
            if session.is_deleted():
                await self.repository.delete_by_id(session_id)

    def get_validity(self):
        return datetime.utcnow() + self.session_validity

    async def store_session(self, session: Session) -> Session:
        await self.repository.insert(session)

        return session

    def add_to_response(self, response: Response, session: Session):
        self.client_store.add_to_response(response, session)

    def remove_from_response(self, response: Response):
        self.client_store.remove_from_response(response)
