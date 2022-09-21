import smtplib
from datetime import (
    datetime,
    timedelta
)
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from logging import Logger
from smtplib import SMTPException
from typing import (
    List,
    Optional
)

from maio.lib.configs.email import EmailConfig


class ConnectionException(Exception):
    __slots__ = ()


class EmailServiceException(Exception):
    __slots__ = ()


class EmailConnection:
    __slots__ = ('config', 'server', 'valid_till', 'logger')

    def __init__(self, config: EmailConfig, logger: Logger):
        self.config = config
        self.server = None
        self.valid_till = None
        self.logger = logger

    def connect(self):
        try:
            if not self.server or not self.is_valid():
                self.server = smtplib.SMTP(self.config.server)
                self.valid_till = datetime.utcnow() + timedelta(seconds=self.config.valid_interval)

                if self.config.tls:
                    if self.logger:
                        self.logger.info("Email connection will use TLS")
                    self.server.starttls()

                if self.config.username:
                    if self.logger:
                        self.logger.info("Email connection will use authentication")
                    self.server.login(self.config.username, self.config.password)

            return self.server
        except SMTPException as exception:
            if self.logger:
                self.logger.error(f"Got exception while trying to connect: {exception}")
            raise ConnectionException() from exception

    def is_valid(self) -> bool:
        return ((self.valid_till is not None) and
                (self.valid_till > datetime.utcnow()))

    def send(self, from_address: str, receivers: List[str], body: str) -> bool:
        try:
            server = self.connect()
            send_errs = server.sendmail(from_address, receivers, body)
            if self.logger and send_errs:
                self.logger.warning(f"Got errors from sending emails: {len(send_errs)}/{len(receivers)} failed")
                return False
            return True
        except SMTPException as exception:
            raise ConnectionException() from exception


class Mail:
    __slots__ = ('message', 'receivers')

    def __init__(self,
                 from_name: str, from_address: str, reply_address: str, to_address: str,
                 topic: str, html_body: str, plain_body: Optional[str] = None, encoding: str = 'utf-8'):
        message = MIMEMultipart('alternative')

        message['Subject'] = topic
        message['From'] = f'{from_name} <{from_address}>'
        message['To'] = to_address

        if reply_address:
            message['reply-to'] = reply_address

        message.attach(MIMEText(plain_body, 'plain', encoding))
        message.attach(MIMEText(html_body, 'html', encoding))

        self.message = message
        self.receivers = [to_address]

    def to_str(self):
        return self.message.as_string()


class EmailService:
    __slots__ = ('connection', 'email_config', 'logger')

    def __init__(self, config: EmailConfig, logger: Logger):
        self.connection = EmailConnection(config, logger)
        self.email_config = config

    def check_connection(self) -> bool:
        if self.connection:
            try:
                self.connection.connect()
                return True
            except Exception:
                pass
        return False

    def send_mail(self,
                  to_address: str,
                  topic: str,
                  html_body: str,
                  plain_body: str,

                  from_name: str = None,
                  from_address: str = None,
                  reply_address: str = None) -> bool:
        try:
            if not from_name:
                from_name = self.email_config.from_name

            if not from_address:
                from_address = self.email_config.from_address

            if not reply_address:
                reply_address = self.email_config.reply_address

            mail = Mail(from_name, from_address, reply_address, to_address, topic, html_body, plain_body)

            return self.connection.send(from_address, mail.receivers, mail.to_str())

        except ConnectionException as exception:
            raise EmailServiceException from exception
