from app.core.dynamic_model import DynamicValidationModel, get_field_rules
from app.core.decorators import body_rule

class UserCreateSchema(DynamicValidationModel):
    email: str = get_field_rules("UserCreateSchema", "email")
    age: int = get_field_rules("UserCreateSchema", "age")
    address: str = get_field_rules("UserCreateSchema", "address", default="Unknown Address")

    @body_rule
    def check_age_address(self) -> None:
        """
        Custom body rule checking if age < 18 and address is 'Unknown Address'.
        Uses getattr since log_only type bypass might leave 'age' missing or as a string.
        """
        age = getattr(self, 'age', None)
        if isinstance(age, int) and age < 18 and self.address == "Unknown Address":
            raise ValueError("Underage users must provide a valid address.")
