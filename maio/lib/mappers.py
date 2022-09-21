from datetime import datetime
from decimal import Decimal
from typing import (
    Any,
    Callable,
    Dict,
    List,
    Optional,
    Set
)
from uuid import UUID

from bson import ObjectId

from maio.lib.errors import (
    ERROR_MISSING,
    Error,
    INVALID_ARRAY,
    INVALID_BOOL,
    INVALID_DATE,
    INVALID_DATETIME,
    INVALID_EMAIL,
    INVALID_FIXED_FLOAT,
    INVALID_NUMBER,
    INVALID_PHONE,
    INVALID_STRING,
    INVALID_UUID,
    too_big,
    too_small
)
from maio.lib.parsers import (
    EMAIL_RE,
    PHONE_RE,
    parse_bool,
    parse_date,
    parse_decimal,
    parse_int,
    parse_object_id,
    parse_uuid
)


def map_str(data: Dict, field_name: str, errors: Dict, required: bool = True, minimal: int = None) -> Optional[str]:
    field_value = data.get(field_name)

    if not field_value:
        if required:
            errors[field_name] = ERROR_MISSING
    elif not isinstance(field_value, str):
        errors[field_name] = INVALID_STRING
    elif minimal and len(field_value) < minimal:
        errors[field_name] = too_small(minimal)

    return field_value


def map_str_enum(data: Dict, field_name: str, errors: Dict, allowed_values: Set[str], required: bool = True) -> Optional[str]:
    field_value = data.get(field_name)

    if not field_value:
        if required:
            errors[field_name] = ERROR_MISSING
    elif not isinstance(field_value, str):
        errors[field_name] = INVALID_STRING
    elif field_value not in allowed_values:
        errors[field_name] = Error("INVALID_KIND", {"expected": f"string from set {allowed_values}"})

    return field_value


def map_object_id(data: Dict, field_name: str, errors: Dict, required: bool = True, error_field: str = None) -> Optional[ObjectId]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name

    if not field_value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        field_value = parse_object_id(field_value)

        if field_value is None:
            errors[error_field] = INVALID_UUID

    return field_value


def map_uuid(data: Dict, field_name: str, errors: Dict, required: bool = True, error_field: str = None) -> Optional[UUID]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name

    if not field_value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        field_value = parse_uuid(field_value)

        if field_value is None:
            errors[error_field] = INVALID_UUID

    return field_value


def map_int(data: Dict, field_name: str, errors: Dict, default: Optional[int] = None, required: bool = True, min_val: int = None, max_val: int = None) -> Optional[int]:
    field_value = data.get(field_name)

    if field_value is None:
        if required:
            errors[field_name] = ERROR_MISSING
        else:
            field_value = default
    else:
        field_value = parse_int(field_value, default=None)

        if field_value is None:
            errors[field_name] = INVALID_NUMBER
        else:
            if min_val and field_value < min_val:
                errors[field_name] = too_small(min_val)
            elif max_val and field_value > max_val:
                errors[field_name] = too_big(max_val)

    return field_value


def map_decimal(data: Dict, field_name: str, errors: Dict, required: bool = True, min_val: Decimal = None, max_val: Decimal = None) -> Optional[Decimal]:
    field_value = data.get(field_name)

    if field_value is None:
        if required:
            errors[field_name] = ERROR_MISSING
    else:
        field_value = parse_decimal(field_value, default=None)

        if field_value is None:
            errors[field_name] = INVALID_FIXED_FLOAT
        else:
            if min_val and field_value < min_val:
                errors[field_name] = too_small(min_val)
            elif max_val and field_value > max_val:
                errors[field_name] = too_big(max_val)

    return field_value


def map_iso_datetime(data: Dict, field_name: str, errors: Dict, required: bool = True, min_val: datetime = None, max_val: datetime = None) -> Optional[datetime]:
    field_value = data.get(field_name)

    if not field_value:
        if required:
            errors[field_name] = ERROR_MISSING
    else:
        field_value = parse_date(field_value)

        if field_value is None:
            errors[field_name] = INVALID_DATETIME
        elif min_val and min_val > field_value:
            errors[field_name] = too_small(min_val)
        elif max_val and max_val < field_value:
            errors[field_name] = too_big(max_val)

    return field_value


def map_date(data: Dict, field_name: str, errors: Dict, required: bool = True, format: str = "%d-%m-%Y", min_val: datetime = None, max_val: datetime = None) -> Optional[datetime]:
    field_value = data.get(field_name)

    if not field_value:
        if required:
            errors[field_name] = ERROR_MISSING
    else:
        try:
            field_value = datetime.strptime(field_value, format)

            if min_val and min_val > field_value:
                errors[field_name] = too_small(min_val)
            elif max_val and max_val < field_value:
                errors[field_name] = too_big(max_val)
        except (ValueError, TypeError):
            errors[field_name] = INVALID_DATE

    return field_value


def map_email(data: Dict, field_name: str, errors: Dict, required: bool = True, domains: Optional[Set] = None, default: bool = None, error_field: str = None) -> Optional[str]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name
    if not field_value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        result = EMAIL_RE.fullmatch(field_value)
        field_value = result.string if result else None

        if not field_value:
            errors[error_field] = INVALID_EMAIL
        elif domains:
            domain = field_value.split("@")[1]
            if domain not in domains:
                errors[error_field] = Error.new("EMAIL.UNSUPPORTED_DOMAIN")

    if field_value is None:
        field_value = default

    return field_value


def map_phone(data: Dict, field_name: str, errors: Dict, required: bool = True, default: bool = None, error_field: str = None) -> Optional[str]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name

    if not field_value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        result = PHONE_RE.fullmatch(field_value)
        field_value = result.string if result else None

        if not field_value:
            errors[error_field] = INVALID_PHONE

    if field_value is None:
        field_value = default

    return field_value


def map_boolean(data: Dict, field_name: str, errors: Dict, required: bool = True, default: bool = None, error_field: str = None) -> Optional[bool]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name

    if field_value is None:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        field_value = parse_bool(field_value)

        if field_value is None:
            errors[error_field] = INVALID_BOOL

    if field_value is None:
        field_value = default

    return field_value


def map_list(data: Dict, field_name: str, mapper: Callable[[Any, str, Dict, bool, Any], Any], errors: Dict, required: bool = True, default=None, error_field: str = None) -> Optional[List]:
    field_value = data.get(field_name)

    error_field = error_field if error_field else field_name
    mapped_values = []

    if field_value is None:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        if not isinstance(field_value, list):
            errors[error_field] = INVALID_ARRAY
        else:
            for index, row in enumerate(field_value):
                value = mapper(row, f'{error_field}.[{index}]', errors, required, default)
                if value is None:
                    value = default
                mapped_values.append(value)

    return mapped_values


def to_uuid(value: Any, error_field: str, errors: Dict, required: bool = True, default: Optional[UUID] = None) -> Optional[UUID]:
    field_value = default
    if not value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        field_value = parse_uuid(value)

        if field_value is None:
            errors[error_field] = INVALID_UUID

    return field_value


def to_object_id(value: Any, error_field: str, errors: Dict, required: bool = True, default: Optional[ObjectId] = None) -> Optional[ObjectId]:
    field_value = default
    if not value:
        if required:
            errors[error_field] = ERROR_MISSING
    else:
        field_value = parse_object_id(value)

        if field_value is None:
            errors[error_field] = INVALID_UUID

    return field_value


def map_list_uuid(data: Dict, field_name: str, errors: Dict, required: bool = True, default=None, error_field: str = None) -> Optional[List[UUID]]:
    return map_list(data, field_name, to_uuid, errors, required, default, error_field)


def map_list_object_id(data: Dict, field_name: str, errors: Dict, required: bool = True, default=None, error_field: str = None) -> Optional[List[ObjectId]]:
    return map_list(data, field_name, to_object_id, errors, required, default, error_field)
