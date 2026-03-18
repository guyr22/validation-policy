# Configuration Settings

MOCK_CONFIG = {
    "UserCreateSchema": {
        "email": {"level": "strict", "pattern": r"^[\w\.-]+@[\w\.-]+\.\w+$"},
        "age": {"level": "log_only", "ge": 18, "le": 120},
        "address": {"level": "soft_launch", "max_length": 50},
        "__body_rules__": [
            {
                "type": "cel",
                "expression": "email != address",
                "level": "strict",
                "error_msg": "Email matched address. Addresses cannot be an email."
            },
            {
                "type": "not_pattern",
                "field": "address",
                "pattern": ".*(hello|shilat).*",
                "level": "strict",
                "error_msg": "Address matches forbidden pattern"
            }
        ]
    }
}
