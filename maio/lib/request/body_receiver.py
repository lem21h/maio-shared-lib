from dataclasses import dataclass
from io import BytesIO
from typing import (
    Dict,
    Optional,
    Set,
)

import magic
from aiohttp import BodyPartReader
from aiohttp.web_request import Request

from maio.lib.request.headers import ContentType


class ReceiverException(BaseException):
    __slots__ = ("code", "additional")

    def __init__(self, code: str, additional: dict = None):
        self.code = f"BODY.{code}"
        self.additional = additional


class BodyUnexpectedUploadException(ReceiverException):
    __slots__ = ()

    def __init__(self, name: str):
        super().__init__("UNEXPECTED", additional={"name": name})


class BodyMissingReceiverException(ReceiverException):
    __slots__ = ()

    def __init__(self):
        super().__init__("MISSING")


class BodyPartMissingReceiver(ReceiverException):
    __slots__ = ()

    def __init__(self):
        super().__init__("MISSING_PART")


class ContentTypeMissingReceiverException(ReceiverException):
    __slots__ = ()

    def __init__(self):
        super().__init__("CONTENT_TYPE.MISSING")


class ContentTypeInvalidReceiverException(ReceiverException):
    __slots__ = ()

    def __init__(self, content_type: str):
        super().__init__("CONTENT_TYPE.INVALID", additional={"expected": content_type})


class BodyTooLargeReceiverException(ReceiverException):
    __slots__ = ()

    def __init__(self, max_size: int):
        super().__init__("TOO_BIG", additional={"max": max_size})


@dataclass
class Upload:
    __slots__ = ('content', 'kind', 'name', 'filename', 'size')
    content: bytes
    kind: str
    name: str
    filename: str
    size: int


class BodyReceiver:
    __slots__ = ('max_size', 'kinds', 'content_type')
    MAX_CHUNK_SIZE = 64 * 1024

    def __init__(self, max_size: int, kinds: Optional[Set[str]], content_type: str = ContentType.MULTIPART_FORM):
        self.max_size = max_size
        self.kinds = kinds
        self.content_type = content_type

    async def receive(self, request: Request, names: Optional[Set[str]] = None) -> Dict[str, Upload]:
        uploads = {}
        content = None
        try:
            if not request.can_read_body:
                raise BodyMissingReceiverException
            if not request.content_type:
                raise ContentTypeMissingReceiverException
            if request.content_type != self.content_type:
                raise ContentTypeInvalidReceiverException(content_type=self.content_type)
            if request.content_length and request.content_length > self.max_size:
                raise BodyTooLargeReceiverException(max_size=self.max_size)

            reader = await request.multipart()

            while True:
                kind = None
                part: BodyPartReader = await reader.next()
                if not part:
                    break

                if names and part.name not in names:
                    raise BodyUnexpectedUploadException(part.name)

                if part.name in uploads:
                    raise BodyUnexpectedUploadException(part.name)

                content_size = 0
                content = BytesIO()

                while not part.at_eof():
                    chunk = await part.read_chunk(self.MAX_CHUNK_SIZE)
                    if not chunk:
                        break

                    if kind is None and self.kinds:
                        kind = magic.from_buffer(chunk)
                        if not kind:
                            raise ContentTypeInvalidReceiverException(content_type=self.content_type)

                        kind = kind.split(",")[0].split(" ")[0]

                        if kind not in self.kinds:
                            raise ContentTypeInvalidReceiverException(content_type=self.content_type)

                    content_size += len(chunk)
                    if content_size > self.max_size:
                        raise BodyTooLargeReceiverException(max_size=self.max_size)

                    content.write(chunk)

                content.seek(0)
                uploads[part.name] = Upload(content.getvalue(), kind, part.name, part.filename, content_size)

            if not uploads:
                raise BodyPartMissingReceiver

            return uploads

        except Exception as exception:
            if content:
                content.close()
            raise exception
