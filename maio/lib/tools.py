import hashlib
from calendar import timegm
from datetime import (
    datetime,
    timezone
)
from math import ceil
from random import (
    choice,
    randint
)
from string import hexdigits
from time import (
    time
)
from typing import Optional
from uuid import (
    UUID,
    getnode,
    uuid4
)

# UUID v1 timestamp is measured from [00:00:00, 1 October 1582][1].
#
# [1]: https://quora.com/Why-UUID-v1-timestamp-measured-from-00-00-00-00-15-October-
_UUID_1_START_DATE = (datetime.utcfromtimestamp(0) - datetime(1582, 10, 15)).total_seconds()


def uuid1_unix_timestamp(uuid: UUID) -> float:
    return uuid.time * 1e-7 - _UUID_1_START_DATE


def uuid1_from_timestamp(ts: datetime, node: Optional[int] = None, clock_seq: Optional[int] = None):
    date = timegm(ts.utctimetuple())
    nanoseconds = (date * 1000000 + ts.microsecond) * 10
    # 0x01b21dd213814000 is the number of 100-ns intervals between the
    # UUID epoch 1582-10-15 00:00:00 and the Unix epoch 1970-01-01 00:00:00.
    timestamp = nanoseconds + 0x01b21dd213814000

    if clock_seq is None:
        import random
        clock_seq = random.getrandbits(14)  # instead of stable storage
    time_low = timestamp & 0xffffffff
    time_mid = (timestamp >> 32) & 0xffff
    time_hi_version = (timestamp >> 48) & 0x0fff
    clock_seq_low = clock_seq & 0xff
    clock_seq_hi_variant = (clock_seq >> 8) & 0x3f
    if node is None:
        node = getnode()
    return UUID(fields=(time_low, time_mid, time_hi_version,
                        clock_seq_hi_variant, clock_seq_low, node), version=1)


def get_uts_high_precision() -> float:
    return time()


def get_unix_timestamp(date: Optional[datetime] = None) -> int:
    """
    Converts date and time to unix timestamp
    If date is not provided then it takes current time and convert it to unix timestamp
    :param date: datetime
    :return: int
    """
    if not date or not isinstance(date, datetime):
        date = datetime.utcnow()
    return timegm(date.utctimetuple())


def from_str_to_unix_timestamp(date_str: str, str_format: str = '%Y-%m-%d') -> Optional[int]:
    try:
        date = datetime.strptime(date_str, str_format)
        return get_unix_timestamp(date)
    except (ValueError, TypeError):
        return None


def unix_timestamp_to_str(timestamp: int, str_format: str = '%Y-%m-%d') -> str:
    return datetime.utcfromtimestamp(timestamp).strftime(str_format)


def date_to_iso(data: datetime) -> str:
    return data.strftime('%Y-%m-%dT%H:%M:%SZ')


def password_hash(password: str, salt: str) -> str:
    return hashlib.sha256(f"{salt}{password}{salt}".encode()).hexdigest()


def password_xor(password: str, secret: str) -> str:
    multiplication = ceil(len(password) / len(secret)) if len(password) > len(secret) else 1
    salt = secret * multiplication
    return bytes(x ^ y for x, y in zip(salt.encode("utf-8"), password.encode("utf-8"))).decode("utf-8")


def generate_token() -> str:
    return "".join([str(randint(100, 999)), str(uuid4()).replace('-', '')])


def xor(password: str, secret: str) -> str:
    if len(password) > len(secret):
        multiplicate = ceil(len(password) / len(secret))
    else:
        multiplicate = 1
    salt = secret * multiplicate
    return bytes(x ^ y for x, y in zip(salt.encode("utf-8"), password.encode("utf-8"))).decode("utf-8")


def token(length: int = 96):
    return "".join([choice(hexdigits) for _ in range(length)])


def apply_utc_timezone(dt: Optional[datetime]) -> Optional[datetime]:
    return dt.replace(tzinfo=timezone.utc) if dt else None
