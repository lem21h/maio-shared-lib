import re
from collections import namedtuple
from datetime import datetime
from typing import (
    Any,
    Dict,
    Iterable,
    List,
    Optional,
    Tuple,
    Type,
    Union,
)

import bson
from pymongo.collation import (
    Collation,
    CollationStrength
)
from pymongo.errors import DuplicateKeyError

from maio.lib.request.pagination import (
    AscDirection,
    DescDirection,
    Direction,
    Sort
)


class RepositoryException(Exception):
    pass


class DataModelException(Exception):
    __slots__ = ('exception', 'data_class')

    def __init__(self, clazz: Type, exception: Exception):
        self.data_class = clazz
        self.exception = exception


class UniqueViolationException(RepositoryException):
    __slots__ = ('index_name',)

    def __init__(self, index_name):
        self.index_name = index_name


class BulkUniqueViolationException(RepositoryException):
    __slots__ = ('failed', 'inserted')

    def __init__(self, inserted, failed):
        self.failed = failed
        self.inserted = inserted


MATCH_FROM_START = 1
MATCH_CONTAINS = 2
MATCH_FROM_END = 3


class DirectionMongoMapper:
    __slots__ = ()
    ASC = 1
    DESC = -1

    TO_DEFINITIONS = {
        AscDirection: ASC,
        DescDirection: DESC
    }

    @classmethod
    def to_mongo(cls, direction: Type[Direction]) -> int:
        return cls.TO_DEFINITIONS[direction]


class MongoSort:
    EN_COLLATION = Collation('en', strength=CollationStrength.SECONDARY, caseLevel=False)

    @classmethod
    def to_mongo(cls, sorting: List[Sort]) -> List[Tuple[str, int]]:
        if sorting:
            return [(sort.field, DirectionMongoMapper.to_mongo(sort.direction)) for sort in sorting]
        else:
            return []


class Mongo:
    __slots__ = ()

    class Pipeline:
        __slots__ = ('_pipeline',)

        class Methods:
            __slots__ = ()

            PROJECT = '$project'
            GROUP = '$group'
            MATCH = '$match'

        def __init__(self):
            self._pipeline = []

        def project(self, definition: Dict) -> 'Mongo.Pipeline':
            self._pipeline.append({self.Methods.PROJECT: definition})
            return self

        def group(self, definition: Dict) -> 'Mongo.Pipeline':
            self._pipeline.append({self.Methods.GROUP: definition})
            return self

        def match(self, definition: Dict) -> 'Mongo.Pipeline':
            self._pipeline.append({self.Methods.MATCH: definition})
            return self

        def get(self):
            return self._pipeline

    @staticmethod
    def update_set(set_changes: Dict, update: Optional[Dict] = None) -> Dict:
        if not update:
            update = {}
        update['$set'] = set_changes

        return update

    @staticmethod
    def match_not_none():
        return {'$ne': None}

    @staticmethod
    def match_in(value_list: List[Any]) -> Dict[str, List]:
        if len(value_list) == 1:
            return value_list[0]
        else:
            return {'$in': value_list}

    @staticmethod
    def match_not_in(value_list: List[Any]) -> Dict[str, List]:
        if len(value_list) == 1:
            return {'$ne': value_list[0]}
        else:
            return {'$nin': value_list}

    @staticmethod
    def join_keys(*fields):
        return '.'.join(fields)

    @staticmethod
    def extract_unique_violation(exception: DuplicateKeyError):
        return exception.details['errmsg'].split(":", 1)[1].split(" ", 2)[1]

    @staticmethod
    def match_date_range(data: Dict[str, Any], field_from: str = None, field_to: str = None) -> Dict[str, Any]:
        date_filtering = {}
        if field_from and isinstance(data.get(field_from), int):
            date_filtering['$gte'] = data[field_from]
        if field_to and isinstance(data.get(field_to), int):
            date_filtering['$lte'] = data[field_to]
        return date_filtering

    @staticmethod
    def match_value_between(min_val: Union[int, float, datetime], max_val: Union[int, float]):
        return {'$gte': min_val, '$lte': max_val}

    @staticmethod
    def match_less_than(val: Union[int, float, datetime], can_equal: bool = True) -> Dict[str, Union[int, float]]:
        return {'$lte' if can_equal else '$lt': val}

    @staticmethod
    def match_greater_than(val: Union[int, float, datetime], can_equal: bool = True) -> Dict[str, Union[int, float]]:
        return {'$gte' if can_equal else '$gt': val}

    @classmethod
    def match(cls, val: Any) -> Dict[str, Any]:
        return {'$eq': val}

    @staticmethod
    def match_string_contains(matching: str, options: Optional[str] = 'i'):
        matching = re.escape(matching)

        str_query = f".*{matching}.*"
        query = {'$regex': str_query}

        if options:
            query['$options'] = options
        return query

    @staticmethod
    def match_string_starts(matching: str, options: Optional[int] = 0):
        matching = re.escape(matching)
        return bson.regex.Regex(f"^{matching}", options)

    @staticmethod
    def match_string_ends(matching: str, options: Optional[str] = 'i') -> Dict:
        matching = re.escape(matching)

        str_query = f"{matching}$"
        query = {'$regex': str_query}

        if options:
            query['$options'] = options
        return query

    @staticmethod
    def max(*args: Iterable[Union[str, int, float]]) -> Dict[str, List]:
        return {"$max": [elem for elem in args]}

    @staticmethod
    def multiply(*args: Iterable[Union[str, int, float]]) -> Dict[str, List]:
        return {"$multiply": [elem for elem in args]}


UpdateOperationResult = namedtuple('UpdateOperationResult', ['found', 'modified'])
