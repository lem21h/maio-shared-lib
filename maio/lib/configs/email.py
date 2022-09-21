from dataclasses import (
    asdict,
    dataclass,
)


@dataclass(frozen=True)
class EmailConfig:
    __slots__ = ('from_name', 'from_address', 'reply_address', 'tls', 'server', 'username', 'password', 'valid_interval')

    from_name: str
    from_address: str
    reply_address: str
    tls: bool
    server: str
    username: str
    password: str
    valid_interval: int

    @classmethod
    def from_json(cls, json_data: dict):
        return EmailConfigJsonMapper.from_json(json_data)

    def to_dict(self) -> dict:
        return asdict(self)


class EmailConfigJsonMapper:
    __slots__ = ()

    class Fields:
        __slots__ = ()
        FROM_NAME = 'fromName'
        FROM_ADDRESS = 'fromAddress'
        REPLY_ADDRESS = 'replyAddress'
        TLS = 'tls'
        SERVER = 'server'
        USERNAME = 'username'
        PASSWORD = 'password'
        VALID_INTERVAL = 'validInterval'

    @classmethod
    def from_json(cls, json_data: dict) -> EmailConfig:
        _ = cls.Fields

        if not isinstance(json_data, dict):
            raise AttributeError("Configuration key 'email' is not JSON object")

        from_name = json_data[_.FROM_NAME]
        from_address = json_data[_.FROM_ADDRESS]
        reply_address = json_data[_.REPLY_ADDRESS]
        tls = json_data[_.TLS]
        server = json_data[_.SERVER]
        username = json_data[_.USERNAME]
        password = json_data[_.PASSWORD]
        valid_interval = int(json_data[_.VALID_INTERVAL])

        return EmailConfig(from_name, from_address, reply_address, tls, server, username, password, valid_interval)
