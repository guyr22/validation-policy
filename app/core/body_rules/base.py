from abc import ABC, abstractmethod
from typing import Dict, Any

class BaseBodyRule(ABC):
    def __init__(self, rule_config: Dict[str, Any]):
        self.rule_config = rule_config
        
    @abstractmethod
    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        """Evaluate the rule against the payload. Returns True if valid, False if invalid."""
        pass
        
    def get_error_message(self) -> str:
        return self.rule_config.get("error_msg", "Dynamic rule failed.")
        
    def get_level(self) -> str:
        return self.rule_config.get("level", "strict")
