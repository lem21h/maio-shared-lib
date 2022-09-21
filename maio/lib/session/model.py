from datetime import datetime
from typing import (
    Type,
    Union
)
from uuid import (
    UUID,
    uuid4
)

from bson import ObjectId


class SessionState:
    __slots__ = ()


class NewSessionState(SessionState):
    __slots__ = ()


class InProgressSessionState(SessionState):
    __slots__ = ()


class DeletedSessionState(SessionState):
    __slots__ = ()


class DefaultSessionContainer:
    __slots__ = ('user_id',)

    def __init__(self, user_id: Union[UUID, ObjectId, int]):
        self.user_id = user_id


class Session:
    __slots__ = ('id', 'valid_till', 'container', 'token', 'state', 'active')
    id: UUID
    valid_till: datetime
    container: DefaultSessionContainer
    token: str
    state: Type[SessionState]
    active: bool

    def __init__(self,
                 id: UUID,
                 valid_till: datetime,
                 container: DefaultSessionContainer,
                 token: str,
                 active: bool,
                 state: Type[SessionState] = InProgressSessionState
                 ):
        self.id = id
        self.valid_till = valid_till
        self.container = container
        self.token = token
        self.state = state
        self.active = active

    def is_valid(self, token):
        return token == self.token

    def is_deleted(self):
        return self.state == DeletedSessionState

    def delete(self):
        self.state = DeletedSessionState

    @property
    def user_id(self) -> UUID:
        return self.container.user_id

    def __repr__(self):
        return f'Session({self.id}: {self.active} valid To {self.valid_till})'

    @classmethod
    def _new(cls, container: DefaultSessionContainer, valid_till: datetime, token: str, active: bool):
        return Session(id=uuid4(),
                       container=container,
                       valid_till=valid_till,
                       token=token,
                       state=NewSessionState,
                       active=active)
