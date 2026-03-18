from typing import Dict, Any
from .base import BaseBodyRule

class UniqueFieldsBodyRule(BaseBodyRule):
    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        fields_to_check = self.rule_config.get("fields", [])
        
        seen_values = set()
        for key, value in data_dict.items():
            if fields_to_check and key not in fields_to_check:
                continue
                
            # Skip empty values to avoid failing valid optional fields
            if value in (None, "", [], {}):
                continue
                
            try:
                if value in seen_values:
                    return False
                seen_values.add(value)
            except TypeError:
                # Unhashable type (e.g., dict or list inside the payload)
                # Since we cannot safely add it to a set without stringifying,
                # we skip it for this basic uniqueness check.
                continue
                
        return True
