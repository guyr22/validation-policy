from .cel_rule import CelBodyRule
from .not_pattern import NotPatternBodyRule
from .unique_fields import UniqueFieldsBodyRule

BODY_RULE_CLASSES = {
    "cel": CelBodyRule,
    "not_pattern": NotPatternBodyRule,
    "unique_fields": UniqueFieldsBodyRule
}

def get_body_rule(rule_config: dict):
    """Factory method to resolve the correct BodyRule class for execution."""
    rule_type = rule_config.get("type", "cel")
    rule_class = BODY_RULE_CLASSES.get(rule_type)
    if rule_class:
        return rule_class(rule_config)
    return None
