from typing import (
    List,
    Set,
)

_SEPARATOR = "#"


def ngram(value: str, length: int) -> List[str]:
    return [value[i:i + length] for i in range(len(value) - length + 1)]


def normalize(value: str) -> str:
    new_value = value.lower()
    new_value = new_value.replace("-", "")
    new_value = new_value.replace("/", "")
    new_value = new_value.replace(".", "")
    new_value = new_value.replace("(", "")
    new_value = new_value.replace(")", "")
    new_value = new_value.replace(" ", "")
    new_value = new_value.replace("#", "")
    new_value = new_value.replace("+", "")

    return new_value


def tokenizer(value: str, prefix: str = None, min_length: int = 3, max_length: int = None) -> Set[str]:
    value = normalize(value)
    if not max_length:
        max_length = len(value) + 1

    tokens = set()

    for i in range(0, max_length - min_length):
        part = value[i:max_length]

        if prefix:
            part = f'{prefix}{_SEPARATOR}{part}'
        tokens.add(part)

    return tokens


def token_search(value: str, prefix: str = None):
    value = normalize(value)

    if prefix:
        value = f"{prefix}{_SEPARATOR}{value}"

    return value
