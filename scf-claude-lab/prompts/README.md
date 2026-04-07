# 🎯 Prompts - System Specifications & Patterns

This folder contains **structured prompt documents** that define the system's business logic, control authoring patterns, and governance rules.

---

## 📂 Files & Importance

### 🟡 **IMPORTANT** (Documentation & Reference)

These are **markdown documents** that document key concepts and workflows. They are **specifications** - not executable code.

#### **P01_control_authoring.md** | Importance: 🌟🌟🌟
- **Purpose**: Specification for control authoring best practices
- **Contains**:
  - Control naming conventions
  - Title format (7-word noun phrases)
  - Statement structure
  - Objective definition rules
  - Quality checklist
- **Used By**: ControlAgent validation; manual control review; training
- **Key Rules**:
  - Titles must be 5-9 words
  - Objectives describe the "why"
  - Statements describe the "what"

---

#### **P02_schema_generation.md** | Importance: 🌟🌟
- **Purpose**: Specification for generating validation schemas from controls
- **Contains**:
  - Schema generation algorithm
  - Required vs. optional fields
  - Type inference rules
  - Constraint definitions
- **Used By**: PolicyAgent for schema generation

---

#### **P03_versioning_supersession.md** | Importance: 🌟🌟🌟
- **Purpose**: Specification for control versioning & lifecycle
- **Contains**:
  - Version numbering scheme (1.0, 1.1, 2.0)
  - When to increment major/minor versions
  - Supersession rules (when v1.0 becomes superseded by v2.0)
  - Backward compatibility strategy
- **Used By**: RegistryAgent for version management; API endpoints
- **Key Rules**:
  - Patch changes → minor version (1.0 → 1.1)
  - Major changes → new version (1.x → 2.0)
  - Old versions preserved forever (immutable history)

---

#### **P04_control_inheritance.md** | Importance: 🌟🌟
- **Purpose**: Specification for control hierarchies and inheritance
- **Contains**:
  - Parent-child relationships
  - Specialization vs. composition
  - Inheritance rules
  - Conflict resolution
- **Used By**: Registry for organizing related controls

---

#### **P05_lifecycle_governance.md** | Importance: 🌟🌟🌟
- **Purpose**: Specification for control status transitions & workflows
- **Contains**:
  - Valid status transitions (draft → active → deprecated → archived)
  - Approval requirements per transition
  - Mandatory fields per status
  - Audit trail requirements
- **Used By**: RegistryAgent for state machine; API endpoints
- **Key Workflow**:
  ```
  draft (creation)
    → active (approved, in use)
    → deprecated (no longer used)
    → archived (historical)
  ```

---

#### **P06_validation_rules.md** | Importance: 🌟🌟
- **Purpose**: Specification for control validation constraints
- **Contains**:
  - Required fields validation
  - Format validation (titles, IDs, etc.)
  - Cross-field validation (control consistency)
  - Business rule validation (domain consistency)
- **Used By**: API validation middleware; PolicyAgent

---

#### **P07_audit_review.md** | Importance: 🌟🌟
- **Purpose**: Specification for audit trail & compliance review
- **Contains**:
  - What must be logged (who, what, when, why)
  - Audit retention policy
  - Review procedures
  - Non-repudiation requirements
- **Used By**: RegistryAgent for audit trail generation; compliance reviews

---

## 📊 How These Prompts Are Used

```
Prompts (Specification Documents)
    ↓
ControlAgent reads to understand rules
    ↓
Validates controls against P01, P06
    ↓
RegistryAgent reads P03, P05
    ↓
Enforces versioning & lifecycle rules
    ↓
PolicyAgent reads P02, P06
    ↓
Generates valid policies
```

---

## 🔗 Related Files

| Prompt | Used By |
|--------|---------|
| P01_control_authoring.md | [../agents/control.py](../agents/control.py) |
| P02_schema_generation.md | [../agents/policy.py](../agents/policy.py) |
| P03_versioning_supersession.md | [../agents/registry.py](../agents/registry.py) |
| P05_lifecycle_governance.md | [../agents/registry.py](../agents/registry.py) |
| P06_validation_rules.md | [../api/schemas.py](../api/schemas.py) |
| P07_audit_review.md | [../agents/models.py](../agents/models.py) |

---

## ✅ Validation

All prompts are validated against [../schemas/prompt.schema.json](../schemas/prompt.schema.json):

```bash
python tools/validate_prompts.py prompts/*.md
```

---

## 📖 Reading Guide

Start with:
1. **P01** - Understand control structure
2. **P05** - Understand control lifecycle
3. **P03** - Understand versioning
4. Then read P02, P04, P06, P07 as needed
