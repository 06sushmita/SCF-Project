ROLE:
You are a platform architect.

INPUT:
Control definition (YAML):
{{CONTROL_YAML}}

TASK:
Generate a JSON Schema for this control suitable for:
- Validation
- Versioning
- Inheritance

REQUIREMENTS:
- Enforce lifecycle states
- Mark required vs optional fields
- Allow inheritance metadata

OUTPUT:
Valid JSON Schema only.
