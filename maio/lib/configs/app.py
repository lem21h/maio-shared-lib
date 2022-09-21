import json
import multiprocessing
from dataclasses import dataclass
from datetime import datetime
from typing import (
    Any,
    Dict,
    Set
)


@dataclass(frozen=True)
class DomainConfig:
    __slots__ = ('base', 'headers', 'origins')
    base: str
    headers: Set[str]
    origins: Set[str]

    @classmethod
    def from_json(cls, json_config: dict):
        return DomainConfigJsonMapper.from_json(json_config)


@dataclass(frozen=True)
class ServerConfig:
    __slots__ = ('keep_alive', 'reload', 'max_requests', 'worker_class', 'workers', 'port', 'ip', 'reuse_port', 'worker_timeout', 'name')

    ip: str
    port: int
    workers: int
    worker_class: str
    keep_alive: int
    max_requests: int
    reload: bool
    reuse_port: bool
    worker_timeout: int
    name: str

    def to_gunicorn_config(self) -> Dict[str, Any]:
        return {
            "bind": f"{self.ip}:{self.port}",
            "workers": self.workers,
            "worker_class": self.worker_class,
            "max_requests": self.max_requests,
            "reload": self.reload,
            "keepalive": self.keep_alive,
            "reuse_port": self.reuse_port,
            "timeout": self.worker_timeout
        }

    @classmethod
    def from_json(cls, json_config: dict):
        return ServerConfigJsonMapper.from_json(json_config)


class AppConfig:
    __slots__ = ()

    def __init__(self):
        pass

    @classmethod
    def from_json(cls, json_config: Dict):
        raise NotImplementedError


class Config:
    __slots__ = ('server_config', 'domain_config', 'app_config', 'start_time', 'version')

    class Fields:
        __slots__ = ()
        SERVER = 'server'
        DOMAIN = 'domain'
        APP = 'app'

        VERSION = 'version'

    server_config: ServerConfig
    domain_config: DomainConfig
    app_config: AppConfig

    start_time: datetime
    version: str

    def __init__(self):
        self.start_time = datetime.utcnow()

    @classmethod
    def from_file(cls, file):
        json_config = json.load(file.config)

        return cls().from_dict(json_config)

    def from_dict(self, json_config: Dict):
        _ = self.Fields
        try:
            self.server_config = ServerConfig.from_json(json_config[_.SERVER])
        except Exception as exception:
            raise RuntimeError(f'Server definition error {exception}')
        try:
            self.domain_config = DomainConfig.from_json(json_config[_.DOMAIN])
        except Exception as exception:
            raise RuntimeError(f'Domain definition error {exception}')
        try:
            self.app_config = AppConfig.from_json(json_config[_.APP])
        except Exception as exception:
            pass
        self.version = json_config.get(_.VERSION)

        return self


class DomainConfigJsonMapper:
    __slots__ = ()

    class Fields:
        __slots__ = ()
        BASE = 'base'
        HEADERS = 'headers'
        ORIGINS = 'origins'

    @classmethod
    def from_json(cls, json_config: dict) -> DomainConfig:
        _ = cls.Fields

        base = json_config.get(_.BASE, "")
        headers = set(json_config.get(_.HEADERS, []))
        origins = set(json_config.get(_.ORIGINS, []))

        return DomainConfig(base, headers, origins)


class ServerConfigJsonMapper:
    class Fields:
        __slots__ = ()
        NAME = 'name'
        PORT = "port"
        IP = "ip"
        WORKERS = "workers"
        WORKER_CLASS = "workerClass"
        MAX_REQUESTS = "maxRequest"
        KEEP_ALIVE = "keepAlive"
        RELOAD = "reload"
        REUSE_PORT = "reusePort"
        WORKER_TIMEOUT = 'workerTimeout'

    class Defaults:
        __slots__ = ()
        WORKER_CLASS = "aiohttp.GunicornUVLoopWebWorker"
        WORKER_TIMEOUT = 600
        MAX_REQUESTS = 0
        KEEP_ALIVE = 2
        RELOAD = False
        REUSE_PORT = True
        NAME = 'Unwanted HTTP Server'

    @classmethod
    def from_json(cls, json_data: dict) -> ServerConfig:
        _ = cls.Fields

        ip = json_data[_.IP]
        port = int(json_data[_.PORT])
        workers = int(json_data.get(_.WORKERS, multiprocessing.cpu_count()))
        worker_class = json_data.get(_.WORKER_CLASS, cls.Defaults.WORKER_CLASS)
        keep_alive = int(json_data.get(_.KEEP_ALIVE, cls.Defaults.KEEP_ALIVE))
        max_requests = int(json_data.get(_.MAX_REQUESTS, cls.Defaults.MAX_REQUESTS))
        reload = json_data.get(_.RELOAD, cls.Defaults.RELOAD)
        reuse_port = json_data.get(_.REUSE_PORT, cls.Defaults.REUSE_PORT)
        worker_timeout = int(json_data.get(_.WORKER_TIMEOUT, cls.Defaults.WORKER_TIMEOUT))
        name = json_data.get(_.NAME, cls.Defaults.NAME)

        return ServerConfig(
            ip=ip, port=port,
            workers=workers,
            worker_class=worker_class,
            keep_alive=keep_alive,
            max_requests=max_requests,
            reload=reload,
            reuse_port=reuse_port,
            worker_timeout=worker_timeout,
            name=name
        )
