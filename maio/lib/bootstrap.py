import argparse
import logging
from typing import Type

import gunicorn.app.base

from maio.lib.configs.app import (
    Config,
    ServerConfig
)


class Application:
    __slots__ = ('config',)

    def __init__(self, config: Config):
        self.config = config

    def run(self):
        raise NotImplementedError


class Server(gunicorn.app.base.BaseApplication):
    def init(self, parser, opts, args):
        raise NotImplemented

    def __init__(self, application, server_config: ServerConfig):
        self.server_config = server_config.to_gunicorn_config()
        self.application = application
        super().__init__()

    def load_config(self):
        for key, value in self.server_config.items():
            self.cfg.set(key.lower(), value)

    def load(self):
        return self.application.run


class Bootstrap:
    __slots__ = ('application', 'config', 'parser')

    def __init__(self, application: Type[Application], config: Type[Config]):
        self.application = application
        self.config = config
        self.parser = argparse.ArgumentParser()
        self.parser.add_argument('--config',
                                 default="config.json",
                                 type=argparse.FileType('r'),
                                 dest='config',
                                 help='JSON configuration file')
        self.parser.add_argument("--log",
                                 default="INFO",
                                 type=str,
                                 dest="log",
                                 help="log level")

    def run(self):
        cmd_args = self.parser.parse_args()

        if cmd_args:
            logging.basicConfig(level=cmd_args.log)
            config = self.config.from_file(cmd_args)

            app = self.application(config)
            Server(app, config.server_config).run()
        else:
            self.parser.print_usage()
