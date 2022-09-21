from datetime import datetime
from typing import (
    Any,
    Dict,
    Optional,
    Type
)
from uuid import UUID

from pymongo.database import Database

from maio.lib.repository import Mongo
from maio.lib.session.model import (
    DefaultSessionContainer,
    Session
)


class DefaultContainerSessionMongoMapper:
    __slots__ = ()

    class Fields:
        USER_ID = 'user_id'

    @classmethod
    def from_mongo(cls, data: Dict) -> DefaultSessionContainer:
        _ = cls.Fields
        return DefaultSessionContainer(data[_.USER_ID])

    @classmethod
    def to_mongo(cls, data: DefaultSessionContainer) -> Dict:
        _ = cls.Fields

        return {
            _.USER_ID: data.user_id
        }


class AbstractSessionMongoMapper:
    __slots__ = ()
    __session_class__ = Session

    class Fields:
        __slots__ = ()
        ID = '_id'
        CONTAINER = 'container'
        VALID_TILL = 'valid_till'
        TOKEN = 'token'
        ACTIVE = 'active'

    @classmethod
    def from_mongo_container(cls, data_container: Any) -> Any:
        raise NotImplementedError

    @classmethod
    def from_mongo(cls, data: Dict) -> Session:
        _ = cls.Fields

        return cls.__session_class__(data[_.ID],
                                     data[_.VALID_TILL],
                                     cls.from_mongo_container(data[_.CONTAINER]),
                                     data[_.TOKEN],
                                     data[_.ACTIVE])

    @classmethod
    def to_mongo_container(cls, container: Any) -> Dict:
        raise NotImplementedError

    @classmethod
    def to_mongo(cls, session: Session) -> Dict:
        _ = cls.Fields

        return {
            _.ID: session.id,
            _.VALID_TILL: session.valid_till,
            _.CONTAINER: cls.to_mongo_container(session.container),
            _.TOKEN: session.token,
            _.ACTIVE: session.active
        }


class SessionMongoRepository:
    __slots__ = ('collection', 'mapper_class')

    __collection__ = "sessions"

    def __init__(self, database: Database, mapper_class: Type[AbstractSessionMongoMapper] = AbstractSessionMongoMapper):
        self.collection = database.get_collection(self.__collection__)
        self.mapper_class = mapper_class

    async def get_by_id(self, session_id: UUID) -> Optional[Session]:
        _ = self.mapper_class.Fields

        query = {
            _.ID: session_id
        }

        result = await self.collection.find_one(query)

        if result:
            return self.mapper_class.from_mongo(result)

    async def delete_by_id(self, session_id: UUID) -> bool:
        _ = self.mapper_class.Fields

        query = {
            _.ID: session_id
        }

        result = await self.collection.delete_one(query)

        return result.deleted_count == 1

    async def update_active_valid_till_by_id(self, valid_till: datetime, session_id: UUID) -> Optional[Session]:
        _ = self.mapper_class.Fields

        query = {
            _.ID: session_id,
            _.VALID_TILL: {'$gte': datetime.utcnow()},
            _.ACTIVE: True
        }

        update = Mongo.update_set({_.VALID_TILL: valid_till})

        result = await self.collection.find_one_and_update(query, update)

        if result:
            return self.mapper_class.from_mongo(result)

    async def insert(self, session: Session):
        data = self.mapper_class.to_mongo(session)

        result = await self.collection.insert_one(data)

        return result.inserted_id
