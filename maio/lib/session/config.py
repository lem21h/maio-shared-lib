from typing import Optional

from maio.lib.configs.mongo import (
    MongoConfig,
    MongoJsonMapper
)


class SessionConfig:
    __slots__ = ('mongo', 'cookie_name', 'cookie_valid', 'secure_token', 'session_valid', 'cookie_secure', 'cookie_samesite')
    mongo: MongoConfig
    cookie_name: str
    cookie_valid: int
    secure_token: str
    session_valid: int
    cookie_secure: bool
    cookie_samesite: Optional[str]

    def __init__(self,
                 mongo: MongoConfig,
                 cookie_name: str,
                 cookie_valid: int,
                 secure_token: str,
                 session_valid: int,
                 cookie_secure: bool,
                 cookie_samesite: Optional[str] = None):
        self.mongo = mongo
        self.cookie_secure = cookie_secure
        self.cookie_name = cookie_name
        self.cookie_valid = cookie_valid
        self.secure_token = secure_token
        self.session_valid = session_valid
        self.cookie_samesite = cookie_samesite

    @classmethod
    def from_json(cls, json_config: dict):
        return SessionConfigJsonMapper.from_json(json_config)


class SessionConfigJsonMapper:
    __slots__ = ()

    class Fields:
        __slots__ = ()
        MONGO = "mongo"
        COOKIE_NAME = "cookieName"
        COOKIE_SECURE = "cookieSecure"
        COOKIE_VALID = "cookieValid"
        COOKIE_SAMESITE = 'cookieSameSite'
        SECURE_TOKEN = "secureToken"
        SESSION_VALID = "sessionValid"

    @classmethod
    def from_json(cls, json_config: dict) -> SessionConfig:
        _ = cls.Fields
        mongo = MongoJsonMapper.from_json(json_config.get(_.MONGO))
        cookie_name = json_config.get(_.COOKIE_NAME)
        cookie_valid = int(json_config.get(_.COOKIE_VALID))
        cookie_secure = json_config.get(_.COOKIE_SECURE, True)
        cookie_samesite = json_config.get(_.COOKIE_SAMESITE)
        secure_token = json_config.get(_.SECURE_TOKEN)
        session_valid = int(json_config.get(_.SESSION_VALID))

        return SessionConfig(mongo, cookie_name, cookie_valid, secure_token, session_valid, cookie_secure, cookie_samesite)
