import html
import random
import re
import string
import time
from calendar import timegm
from datetime import (
    datetime,
    timedelta,
)
from decimal import (
    Decimal,
    DecimalException,
)
from functools import singledispatch
from typing import (
    Any,
    Dict,
    Optional,
    Pattern,
    Union,
)
from uuid import (
    UUID,
)

from bson import ObjectId

PHONE_RE = re.compile(r'^\+?([0-9 ])+$')
PHONE_9_RE = re.compile(r'^\+?([0-9 ]){9}$')
TAG_RE = re.compile(r'(<!--.*?-->|<[^>]*>)')
EMAIL_RE = re.compile(r'(^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$)')
CHARACTERS = string.ascii_letters + string.digits


def random_printable(length: int) -> str:
    return ''.join([random.choice(CHARACTERS) for _ in range(0, length)])


def parse_uuid(str_uuid: str, default=None) -> Optional[UUID]:
    try:
        if isinstance(str_uuid, bytes):
            str_uuid = str_uuid.decode()
        if not isinstance(str_uuid, UUID):
            return UUID(str_uuid)
        else:
            return str_uuid
    except (ValueError, TypeError, AttributeError):
        return default


def parse_object_id(object_id: str, default: ObjectId = None) -> Optional[ObjectId]:
    try:
        if object_id:
            return ObjectId(object_id.decode() if isinstance(object_id, bytes) else object_id)
    except (ValueError, TypeError, AttributeError):
        pass
    return default


country_to_phone: Dict[str, Pattern] = {
    'PL': PHONE_9_RE,
    "POL": PHONE_9_RE
}


def parse_phone_number(phone_number: str, country: str = None) -> Optional[str]:
    global country_to_phone
    try:
        pattern = country_to_phone.get(country, PHONE_RE)
        result = pattern.match(phone_number)

        if result:
            return result.string
    except TypeError:
        return None


def remove_tags(text: str) -> str:
    if not text or not isinstance(text, str):
        return ''
    return html.escape(TAG_RE.sub('', text))


@singledispatch
def parse_bool(value: Any, default=None) -> Optional[bool]:
    return default


@parse_bool.register(int)
def parse_bool_int(value: int, default=None) -> Optional[bool]:
    if value == 1:
        return True
    elif value in {-1, 0}:
        return False
    else:
        return default


@parse_bool.register(str)
def parse_bool_str(value: str, default=None) -> Optional[bool]:
    value = value.lower().strip()
    if value in {"1", "true"}:
        return True
    elif value in {"0", "false"}:
        return False
    else:
        return default


@parse_bool.register(bool)
def parse_bool_bool(value: bool, default=None) -> Optional[bool]:
    return value


def parse_int(value: Union[float, int, str], default: Optional[int] = 0):
    try:
        out = int(value)
    except (ValueError, TypeError):
        out = default
    return out


def parse_decimal(value: Union[float, int, str], default: Optional[Decimal] = None):
    try:
        out = Decimal(value)
        return out

    except DecimalException:
        return default


def parse_float(value: Union[float, int, str], default: Optional[Union[float, int]] = 0):
    try:
        out = float(value)
    except (ValueError, TypeError):
        out = default
    return out


def parse_date(date_stamp: str, default=None) -> datetime:
    try:
        return iso8601.parse_date(date_stamp)
    except (ValueError, iso8601.ParseError, TypeError):
        return default


def parse_date_to_unix_ts(date_stamp, default=None):
    dt = parse_date(date_stamp)
    if dt:
        return get_unixtimestamp(dt)
    else:
        return default


def get_uts_high_precision() -> float:
    return time.time()


def get_unixtimestamp(date: datetime = None) -> int:
    """
    Converts date and time to unix timestamp
    If date is not provided then it takes current time and convert it to unix timestamp
    :param date: datetime
    :return: int
    """
    if not date or not isinstance(date, datetime):
        date = datetime.utcnow()
    return timegm(date.utctimetuple())


def from_str_to_unixtimestamp(date_str: str, str_format='%Y-%m-%d') -> Optional[int]:
    try:
        date = datetime.strptime(date_str, str_format)
        return get_unixtimestamp(date)
    except (ValueError, TypeError):
        return None


def last_day_of_month(any_day):
    next_month = any_day.replace(day=28) + timedelta(days=4)  # this will never fail
    return next_month - timedelta(days=next_month.day)


def unixtimestamp_to_str(timestamp, str_format='%Y-%m-%d'):
    return datetime.utcfromtimestamp(timestamp).strftime(str_format)


def uts_to_str(timestamp=None, str_format='%Y-%m-%dT%H:%M:%SZ'):
    return unixtimestamp_to_str(timestamp, str_format) if timestamp else ''


def date_to_iso(data: datetime) -> str:
    return data.strftime('%Y-%m-%dT%H:%M:%SZ')
