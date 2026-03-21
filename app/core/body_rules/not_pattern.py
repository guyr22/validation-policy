import re
from typing import Dict, Any
from .base import BaseBodyRule

class NotPatternBodyRule(BaseBodyRule):
    def __init__(self, rule_config: Dict[str, Any]):
        super().__init__(rule_config)
        self._field_name = self.rule_config.get("field")
        self._pattern_str = self.rule_config.get("pattern")
        self._regex = None

        # Precompile regex so we don't pay compile cost per alert.
        if self._field_name and self._pattern_str:
            self._regex = re.compile(self._pattern_str)

    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        if self._field_name and self._regex and self._field_name in data_dict:
            val = data_dict[self._field_name]
            if val is not None:
                if self._regex.search(str(val)):
                    return False
        return True
