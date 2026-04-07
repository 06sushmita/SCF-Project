# 📐 Schemas - Data Validation & Structure

This folder contains **JSON schema definitions** that validate data structure, types, and constraints across the platform.

---

## 📂 Files & Importance

### 🟡 **IMPORTANT** (Data Governance)

#### **prompt.schema.json** | Importance: 🌟🌟🌟
- **Purpose**: JSON Schema for validating prompt/instruction structure
- **Format**: JSON Schema (draft 7)
- **Usage**: Validates `.md` prompts against defined schema
- **Validates**:
  - Prompt sections (title, context, requirements)
  - Required fields
  - Type constraints (strings, arrays, objects)
  - Enum values (allowed choices)
- **Used By**: [../tools/validate_prompts.py](../tools/validate_prompts.py)
- **Critical for**: Ensuring consistent prompt structure across [../prompts/](../prompts/)
- **Example Validation**:
  ```bash
  python tools/validate_prompts.py prompts/P01_control_authoring.md
  # Output: ✅ Valid or ❌ Invalid with error details
  ```

---

## 🔗 Related Files

| File | Relationship |
|------|--------------|
| [../prompts/](../prompts/) | Files validated by `prompt.schema.json` |
| [../tools/validate_prompts.py](../tools/validate_prompts.py) | Uses this schema for validation |

---

## 📐 Schema Extension

To add a new schema:
1. Create `new_schema.json` in this folder
2. Define JSON Schema structure
3. Add validator to [../tools/](../tools/)
4. Update this README
