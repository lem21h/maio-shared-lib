from datetime import datetime

from bson import ObjectId


class BasicIdModel:
    __slots__ = ('id',)

    id: ObjectId

    def __init__(self, id: ObjectId):
        self.id = id

    @property
    def created_date(self) -> datetime:
        return self.id.generation_time


class BasicLoginModel(BasicIdModel):
    __slots__ = ('username', 'password', 'salt')

    username: str
    password: str
    salt: str

    def __init__(self, id: ObjectId, username: str, password: str, salt: str):
        super().__init__(id)
        self.username = username
        self.password = password
        self.salt = salt
