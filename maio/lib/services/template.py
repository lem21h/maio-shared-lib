import string
from typing import (
    Any,
    Dict,
    Optional
)

from maio.lib.configs.template import TemplateConfig


class TemplateService:
    __slots__ = ('config',)

    ALLOWED_KEY_CHARS = string.ascii_uppercase + string.digits + '_-'

    def __init__(self, config: TemplateConfig):
        self.config: TemplateConfig = config

    def _load_template(self, template_name: str) -> str:
        with open(f'{self.config.base_path}/{template_name}', 'r') as fp:
            template = fp.read()
        return template

    def get(self, template_name: str, values: Optional[Dict[str, Any]], replacement_key: Optional[str] = None) -> str:
        template = self._load_template(template_name)

        r_values: Optional[Dict[str, Any]] = self.config.replacement_values.get(replacement_key)
        if r_values:
            r_values.update(values)
        else:
            r_values = values

        return self._render_template(template, r_values)

    REPLACEMENT_CHAR_OPEN = '{'
    REPLACEMENT_CHAR_CLOSE = '}'

    def _render_template(self, template: str, replacement_values: Dict[str, Any]) -> str:
        key = []
        output = []
        max_len = len(template)
        cur_len = 0
        state = 0

        _A = self.ALLOWED_KEY_CHARS
        _RC = self.REPLACEMENT_CHAR_CLOSE
        _RO = self.REPLACEMENT_CHAR_OPEN

        while cur_len < max_len:
            cur_char = template[cur_len]
            if state == 1:
                if cur_char in _A:
                    key.append(cur_char)
                    cur_len += 1
                elif cur_char == _RC and cur_len + 1 < max_len and template[cur_len + 1] == _RC:
                    # end replacement
                    # trigger replacement
                    state = 0
                    key = ''.join(key)
                    output.append(str(replacement_values.get(key, f'<{key}>')))
                    key = []
                    cur_len += 2
                else:
                    cur_len += 1
                    state = 0
            elif state == 0 and cur_char == _RO and cur_len + 1 < max_len and template[cur_len + 1] == _RO:
                # key reading
                cur_len += 2
                state = 1
            else:
                output.append(cur_char)
                cur_len += 1
        return ''.join(output)
