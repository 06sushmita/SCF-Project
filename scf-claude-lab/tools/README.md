# 🛠️ Tools - Utility Scripts & Validators

This folder contains **utility scripts** for maintenance, validation, and operational tasks.

---

## 📂 Files & Importance

### 🟡 **IMPORTANT** (Operations & Quality)

#### **validate_prompts.py** | Importance: 🌟🌟
- **Purpose**: Validates prompt files against JSON schema
- **Functionality**:
  - Reads all `.md` files in [../prompts/](../prompts/)
  - Validates against [../schemas/prompt.schema.json](../schemas/prompt.schema.json)
  - Reports errors and warnings
  - Checks consistency
- **Usage**:
  ```bash
  # Validate single prompt
  python tools/validate_prompts.py prompts/P01_control_authoring.md
  
  # Validate all prompts
  python tools/validate_prompts.py prompts/*.md
  
  # Validate and fix
  python tools/validate_prompts.py --fix prompts/*.md
  ```
- **Output**:
  ```
  ✅ P01_control_authoring.md - VALID
  ❌ P02_schema_generation.md - ERROR: Missing 'version' field
  ```
- **Used By**: CI/CD pipeline, pre-commit hooks, manual verification
- **Critical for**: Ensuring prompt consistency and quality

---

## 🚀 Usage Examples

### **CI/CD Integration**:
```yaml
# GitHub Actions / GitLab CI
validate_prompts:
  script:
    - python tools/validate_prompts.py prompts/*.md
```

### **Pre-Commit Hook**:
```bash
#!/bin/bash
python tools/validate_prompts.py prompts/*.md || exit 1
```

---

## 🔗 Related Files

| File | Used For |
|------|----------|
| [../prompts/](../prompts/) | Validation target |
| [../schemas/prompt.schema.json](../schemas/prompt.schema.json) | Validation schema |

---

## 📝 Future Tools

Consider adding:
- `validate_controls.py` – Validate control registry
- `migrate_policies.py` – Migrate policies between versions
- `audit_report.py` – Generate compliance audit reports
- `backup_registry.py` – Backup controls registry
