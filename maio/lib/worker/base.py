import argparse
import logging
import signal
from logging import Logger
from typing import (
    Dict,
    Type
)

from maio.lib.configs.app import AppConfig


class WorkerApplication:
    __slots__ = ('config', 'terminated', 'interrupted', 'logger')

    def __init__(self, config: AppConfig, logger: Logger):
        self.config = config
        self.terminated = False
        self.interrupted = False
        self.logger = logger

        signal.signal(signal.SIGTERM, self.signal_term)
        signal.signal(signal.SIGINT, self.signal_int)

    def run(self):
        raise NotImplementedError

    def signal_term(self, *args):
        self.logger.info("Received signal terminate")
        self.terminated = True

    def signal_int(self, *args):
        self.logger.info("Received signal interrupted")
        self.interrupted = True


class WorkerBootstrap:
    __slots__ = ('applications', 'application', 'config', 'parser')

    def __init__(self, applications: Dict[str, Type[WorkerApplication]], config: Type[AppConfig]):
        self.config = config
        self.parser = argparse.ArgumentParser()

        if len(applications) > 1:
            self.application = None
            self.applications = applications
            self.parser.add_argument('command', choices=list(applications.keys()))
        else:
            self.applications = None
            self.application = applications.popitem()[1]

        self.parser.add_argument('--config',
                                 default="config.json",
                                 type=argparse.FileType('r'),
                                 required=True,
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
            config = self.config.from_json(cmd_args.config)

            application = self.applications.get(cmd_args.command) if self.applications else self.application
            application(config).run()

        else:
            self.parser.print_usage()
