import multiprocessing
from dataclasses import dataclass


@dataclass(frozen=True)
class MongoConfig:
    __slots__ = ('uuid', 'max_conn', 'uri')

    uri: str
    max_conn: int
    uuid: str

    @classmethod
    def from_json(cls, json_config: dict):
        return MongoJsonMapper.from_json(json_config)

    def to_dict(self):
        return MongoDictMapper.to_dict(self)


class MongoJsonMapper:
    class Json:
        __slots__ = ()
        CONNECTION_URI = "connectionUri"
        POOL_SIZE = "maxPoolSize"
        UUID = "uuid"

    class DEFAULTS:
        __slots__ = ()
        CONNECTIONS = 100
        UUID = "standard"

    @classmethod
    def from_json(cls, json_data: dict) -> MongoConfig:
        _ = cls.Json
        default = cls.DEFAULTS

        if not isinstance(json_data, dict):
            raise AttributeError("Configuration key 'mongo' is not JSON object")

        uri = json_data[_.CONNECTION_URI]
        max_conn = int(json_data.get(_.POOL_SIZE)) if _.POOL_SIZE in json_data else multiprocessing.cpu_count() * default.CONNECTIONS
        uuid = json_data.get(_.UUID, default.UUID)

        return MongoConfig(uri, max_conn, uuid)


class MongoDictMapper:
    class Dict:
        CONNECTION_URI = "connectionUri"
        POOL_SIZE = "maxPoolSize"
        UUID = "uuidRepresentation"

    @classmethod
    def to_dict(cls, mongo_config: MongoConfig) -> dict:
        _ = cls.Dict
        return {
            _.CONNECTION_URI: mongo_config.uri,
            _.POOL_SIZE: mongo_config.max_conn,
            _.UUID: mongo_config.uuid
        }
