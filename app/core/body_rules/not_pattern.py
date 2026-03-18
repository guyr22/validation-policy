import re
from typing import Dict, Any
from .base import BaseBodyRule

class NotPatternBodyRule(BaseBodyRule):
    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        field_name = self.rule_config.get("field")
        pattern_str = self.rule_config.get("pattern")
        
        if field_name and pattern_str and field_name in data_dict:
            val = data_dict[field_name]
            if val is not None:
                if re.search(pattern_str, str(val)):
                    return False
        return True
