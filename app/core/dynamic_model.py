import logging
from typing import Any, Callable, Dict, Annotated
import celpy
from pydantic import BaseModel, model_validator, TypeAdapter, ValidationError
from pydantic_core import PydanticUndefined

from app.config.settings import MOCK_CONFIG
from app.services.elastic import send_to_elastic
from app.core.utils import get_dummy_value

logger = logging.getLogger(__name__)

def get_field_rules(schema_name: str, field_name: str, default: Any = PydanticUndefined) -> Any:
    """Helper to inject configuration rules directly into Pydantic Field declarations."""
    from pydantic import Field
    rules = MOCK_CONFIG.get(schema_name, {})
    field_config = rules.get(field_name, {})
    
    if isinstance(field_config, str):
        return Field(default=default) if default is not PydanticUndefined else Field()
        
    kwargs = {k: v for k, v in field_config.items() if k != "level"}
    if default is not PydanticUndefined:
        kwargs["default"] = default
        
    return Field(**kwargs)

def _process_soft_launch_injections(cls: Any, data: dict, rules: dict) -> Dict[str, str]:
    """Pre-processes dictionary to handle soft_launch injections."""
    soft_launch_errors = {}
    for field_name, field_info in cls.model_fields.items():
        rule_config = rules.get(field_name, 'hard')
        base_level = rule_config.get('level', 'hard') if isinstance(rule_config, dict) else rule_config
        
        if base_level != 'soft_launch':
            continue
            
        DynamicType = Annotated[field_info.annotation, *field_info.metadata]
            
        is_invalid = False
        if field_name not in data:
            is_invalid = True
        else:
            try:
                TypeAdapter(DynamicType).validate_python(data[field_name])
            except ValidationError:
                is_invalid = True
                
        if is_invalid:
            soft_launch_errors[field_name] = f"Missing or invalid expected format/rules for '{field_name}'"
            if field_info.default is not PydanticUndefined:
                data[field_name] = field_info.default
            elif getattr(field_info, 'default_factory', None) is not None:
                data[field_name] = field_info.default_factory()
            else:
                data[field_name] = get_dummy_value(field_info.annotation)
                
    return soft_launch_errors


def _handle_validation_error(cls: Any, data: Any, rules: dict, error: ValidationError) -> Any:
    """Handles parsing validation errors and determining if it's a hard fail or log_only wrapper build."""
    schema_name = cls.__name__
    errors = error.errors()
    hard_errors = []
    
    for err in errors:
        loc = err.get('loc', [])
        field_name = loc[0] if loc else None
        rule_config = rules.get(str(field_name), 'hard')
        level = rule_config.get('level', 'hard') if isinstance(rule_config, dict) else rule_config
        
        if level == 'log_only':
            logger.warning(
                f"[LOG_ONLY WARN] Validation failed for {schema_name}.{field_name}. "
                f"Error: {err.get('msg')} -> Payload remains untouched."
            )
        elif level == 'soft_launch':
            pass # Pre-processed and safely handled dummy injection. Ignore cascading errors from dummy values failing strict constraints.
        else:
            hard_errors.append(err)
    
    if hard_errors:
        raise error
    else:
        # If only log_only fields failed, force-build the object to bypass strict-typing
        if isinstance(data, dict):
            instance = cls.model_construct(**data)
            return instance.run_body_rules()
        return cls.model_construct()


class DynamicValidationModel(BaseModel):
    @model_validator(mode='wrap')
    @classmethod
    def wrap_validation(cls, data: Any, handler: Callable[[Any], Any]) -> 'DynamicValidationModel':
        if isinstance(data, dict):
            schema_name = cls.__name__
            rules = MOCK_CONFIG.get(schema_name, {})
            
            soft_launch_errors = _process_soft_launch_injections(cls, data, rules)
            
            if soft_launch_errors:
                send_to_elastic(schema_name, soft_launch_errors)
                
        # Attempt standard validation
        try:
            return handler(data)
        except ValidationError as e:
            rules = MOCK_CONFIG.get(cls.__name__, {})
            return _handle_validation_error(cls, data, rules, e)

    @model_validator(mode='after')
    def run_body_rules(self) -> 'DynamicValidationModel':
        """Scans the config and class for body-level rules and executes them."""
        schema_name = self.__class__.__name__
        config = MOCK_CONFIG.get(schema_name, {})
        body_rules = config.get("__body_rules__", [])
        
        data_dict = self.model_dump()
                            
        for rule_config in body_rules:
            from .body_rules import get_body_rule
            
            rule = get_body_rule(rule_config)
            if not rule:
                logger.warning(f"Unsupported body rule type: {rule_config.get('type')}")
                continue
                
            is_valid = rule.evaluate(data_dict)
            if not is_valid:
                error_msg = rule.get_error_message()
                level = rule.get_level()
                
                if level == "log_only":
                    logger.warning(f"[LOG_ONLY WARN] Body rule failed. Error: {error_msg}")
                else:
                    raise ValueError(error_msg)

        for attr_name in dir(self.__class__):
            attr = getattr(self.__class__, attr_name)
            if getattr(attr, '__is_body_rule__', False):
                method = getattr(self, attr_name)
                method()
        return self
