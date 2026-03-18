import logging
from typing import Dict, Any
import celpy
from .base import BaseBodyRule

logger = logging.getLogger(__name__)

class CelBodyRule(BaseBodyRule):
    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        expr = self.rule_config.get("expression")
        if not expr:
            return True
            
        try:
            env = celpy.Environment()
            ast = env.compile(expr)
            prgm = env.program(ast)
            
            result = prgm.evaluate(data_dict)
            return bool(result)
        except Exception as e:
            logger.error(f"Failing to evaluate CEL expression '{expr}': {e}")
            return False
