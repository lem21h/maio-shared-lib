from builtins import ValueError
from datetime import (
    date,
    datetime
)
from enum import Enum
from typing import (
    Any,
    Callable,
    List,
    Optional,
    Set,
    Tuple,
    Type,
    Union,
)
from uuid import UUID

from aiohttp.web_request import Request
from bson import ObjectId

from maio.lib.parsers import (
    parse_bool,
    parse_date_to_unix_ts,
    parse_int,
    parse_object_id,
    parse_uuid
)
from maio.lib.request.pagination import (
    AscDirection,
    DescDirection,
    Direction,
    Pagination,
    Sort
)


class DirectionRequestMapper:
    __slots__ = ()

    ASC = 'asc'
    DESC = 'desc'

    FROM_DEFINITIONS = {
        ASC: AscDirection,
        DESC: DescDirection
    }

    @classmethod
    def from_str(cls, direction: str) -> Type[Direction]:
        if direction:
            direction = direction.lower()

            return cls.FROM_DEFINITIONS.get(direction)


class DateRange:
    __slots__ = ('begin', 'end')
    begin: Optional[datetime]
    end: Optional[datetime]

    def __init__(self,
                 begin: Optional[datetime] = None,
                 end: Optional[datetime] = None):
        self.begin = begin
        self.end = end

    def __contains__(self, item) -> bool:
        if not isinstance(item, (datetime, date)):
            raise ValueError(f"Cannot compare with {self.__class__.__name__}")

        if self.begin and self.end:
            return self.begin <= item <= self.end

        if self.begin and not self.end:
            return self.begin <= item

        if not self.begin and self.end:
            return item <= self.end

        return False


class QueryParams:
    __slots__ = ('request', 'sort', 'limit', 'page')

    class Fields:
        __slots__ = ()

        SORT = 'sort'
        ORDER = 'order'
        PAGE = 'page'
        LIMIT = 'limit'

    def __init__(self, request: Request, sort: Optional[Sort], limit: int = 0, page: int = 0):
        self.request = request
        self.sort = sort
        self.limit: int = limit
        self.page: int = page

    @classmethod
    def from_request(cls,
                     request: Request,
                     available_sort: Union[List[str], Tuple, Set[str]] = None,
                     default_sort: Optional[Sort] = None,
                     max_limit: int = 50,
                     default_limit: int = 25):
        _ = cls.Fields

        if available_sort:
            sort = request.query.getone(_.SORT, None)
            if sort is None or sort not in available_sort:
                sort = default_sort.field if default_sort else None

            direction = DirectionRequestMapper.from_str(request.query.getone(_.ORDER, None))

            if direction is None:
                direction = default_sort.direction if default_sort else AscDirection
        else:
            sort = None
            direction = None

        try:
            limit = int(request.query.getone(_.LIMIT, default_limit))
            if not (0 < limit <= max_limit):
                limit = default_limit
        except (ValueError, TypeError):
            limit = default_limit

        try:
            page = int(request.query.getone(_.PAGE, 0))
            if 0 > page:
                page = 0
        except (ValueError, TypeError):
            page = 0

        return cls(request, Sort(sort, direction), limit, page)

    def get_sort(self) -> Sort:
        return self.sort

    def get_pagination(self) -> Pagination:
        return Pagination(self.limit, self.page * self.limit)

    def get_bool(self, field_name: str, default: Optional[bool] = None) -> bool:
        return parse_bool(self.request.query.getone(field_name, None), default)

    def get_uuid(self, field_name: str) -> Optional[UUID]:
        return parse_uuid(self.request.query.getone(field_name, None))

    def get_object_id(self, field_name: str) -> Optional[ObjectId]:
        return parse_object_id(self.request.query.getone(field_name, None))

    def get_timestamp(self, field_name: str, default: Optional[str] = None) -> int:
        return parse_date_to_unix_ts(self.request.query.getone(field_name, default))

    def get(self, field_name: str, default: Optional[str] = None, min_len: int = -1) -> Optional[str]:
        value = self.request.query.getone(field_name, default)
        if value and min_len != -1:
            return value if len(value) >= min_len else default
        return value

    def get_int(self, field_name: str, default: Optional[int] = None) -> Optional[int]:
        value = self.request.query.getone(field_name, default)
        if value:
            return parse_int(value, default)
        return None

    def get_enum(self, field_name: str, enum_clazz: Type[Enum], default: Optional = None):
        value = self.request.query.getone(field_name, default)
        if value:
            try:
                return enum_clazz[value.upper()]
            except KeyError:
                return default
        else:
            return None

    def get_list(self, name: str, separator: str = ',', mapper: Optional[Callable[[str], Any]] = None) -> List[str]:
        if mapper:
            return [mapper(element) for element in self.get(name, "").split(separator) if element]
        else:
            return [element for element in self.get(name, "").split(separator) if element]

    def get_date(self, field_name: str, format: str = "%d-%m-%Y", default=None) -> Optional[datetime]:
        value = self.request.query.getone(field_name, None)

        if value:
            try:
                return datetime.strptime(value, format)
            except (ValueError, TypeError):
                return default
        else:
            return default

    def get_date_range(self, field_name: str, format: str = "%d-%m-%Y", default: Optional[DateRange] = None) -> Optional[DateRange]:
        begin = self.get_date(f"{field_name}From", format)
        end = self.get_date(f"{field_name}End", format)

        if begin or end:
            return DateRange(begin, end)
        else:
            return default
