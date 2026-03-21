import logging
from typing import Dict, Any
import celpy
from .base import BaseBodyRule

logger = logging.getLogger(__name__)

class CelBodyRule(BaseBodyRule):
    def __init__(self, rule_config: Dict[str, Any]):
        super().__init__(rule_config)
        self._expr = self.rule_config.get("expression")
        self._prgm = None

        # Precompile CEL expression so we don't do compilation work per alert.
        if self._expr:
            try:
                env = celpy.Environment()
                ast = env.compile(self._expr)
                self._prgm = env.program(ast)
            except Exception as e:
                logger.error(f"Failed to compile CEL expression '{self._expr}': {e}")
                self._prgm = None

    def evaluate(self, data_dict: Dict[str, Any]) -> bool:
        if not self._expr:
            return True
        if self._prgm is None:
            # Expression existed but compilation failed; keep consistent with the old behavior
            # where evaluation would return False on compilation/evaluation exceptions.
            return False
            
        try:
            result = self._prgm.evaluate(data_dict)
            return bool(result)
        except Exception as e:
            logger.error(f"Failing to evaluate CEL expression '{self._expr}': {e}")
            return False
