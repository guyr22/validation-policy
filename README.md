# Dynamic Validation System

Welcome to the Dynamic Validation Pipeline project! This README provides team members a clear overview of how the validation policy system operates.

## 🧠 How Validation Works

The core of this validation system is built upon **Pydantic V2** combined with a dynamic configuration loader. This means validation rules can be changed dynamically without directly altering the Pydantic class schemas.

1. **Configuration (`app/config/settings.py`)**:
   We define our validation rules using `MOCK_CONFIG`. These rules dictate what restrictions apply to each field, including custom constraints like `pattern` matching, bounds (`ge`, `le`), etc.

2. **The Base Model (`app/core/dynamic_model.py`)**:
   All new schemas should inherit from `DynamicValidationModel`. This custom BaseModel automatically wraps Pydantic's validation flow to read our Dynamic rules before and after parsing payloads.
   - It seamlessly handles injecting standard rules into `pydantic.Field`s via `get_field_rules()`.

## ⚙️ Enforcement Levels

Different severity levels can be applied to validation rules to observe payload behaviors in production without breaking APIs immediately:
- **`hard`**: Standard validation. Any failure raises a 422 Unprocessable Entity error.
- **`log_only`**: Validation failures are caught and logged as warnings (`[LOG_ONLY WARN]`), but the application continues processing the payload untouched.
- **`soft_launch`**: Validation failures log the error and attempt to "heal" the payload by injecting dummy/default values, allowing parsing to proceed dynamically (often sending the error context seamlessly to elasticsearch via `send_to_elastic`).

## 🧱 Field Rules vs. Body Rules

There are two primary places validation occurs:
- **Field-level Rules**: Handled iteratively on specific schema attributes (e.g., `email: {"level": "hard", "pattern": "..."}`).
- **Body-level Rules**: Used to validate interdependent fields. 
  - *Dynamic Configuration Config*: Passed in via `__body_rules__` array in `settings` (e.g., CEL rules).
  - *Decorators*: Defined via `@body_rule` methods directly within the Pydantic schema class.

---
*For any structural issues regarding the validation pipeline architecture or rule engines, refer to `app/core/body_rules` to examine or add new custom rule handlers.*
