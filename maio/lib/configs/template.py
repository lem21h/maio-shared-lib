from typing import (
    Any,
    Dict
)


class TemplateConfig:
    __slots__ = ('base_path', 'replacement_values')

    def __init__(self, base_path: str, replacement_values: Dict[str, Any]):
        self.base_path: str = base_path
        self.replacement_values: Dict[str, Any] = replacement_values

    @classmethod
    def from_json(cls, data: Dict[str, Any]):
        return cls(
            base_path=data['basePath'],
            replacement_values=data.get('values')
        )
