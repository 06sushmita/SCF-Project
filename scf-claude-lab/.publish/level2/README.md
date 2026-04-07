# 📑 LEVEL 2 - Control Registry

## Overview

**Level 2** manages controls as versioned, governed assets with lifecycle tracking.

- **Source of Truth**: `level1/controls.yaml`
- **Functionality**: Versioning, lifecycle management, searchability
- **Output**: Registry with version history and lifecycle states

---

## How to Use

### Run Registry

```bash
cd level2
python registry.py
```

### Output

```
📖 LOADING 9 CONTROLS FROM level1/controls.yaml
========================================

✅ Total Controls: 9

📊 BY DOMAIN:
  • Access Control: 9

📊 BY LIFECYCLE STATE:
  • draft: 7
  • approved: 1
  • active: 1

✓ Registry exported to controls/registry_level2.json
```

---

## Key Features

✅ **Reads from control.yaml** – Single source of truth  
✅ **Versioning** – Track all versions (1.0, 1.1, 2.0...)  
✅ **Lifecycle States** – draft → approved → active → deprecated  
✅ **Searchable** – Search by domain, type, keywords  
✅ **Audit Trail** – Track who changed what and when  

---

## Data Model

```json
{
  "control_id": "SCF-001",
  "title": "Procedure For Enrollment / Registration Of Brokers",
  "control_statement": "Procedure for enrollment / registration...",
  "objective": "Ensure only authorised and verified parties...",
  "control_type": "Preventive",
  "control_domain": "Access Control",
  "control_family": "Third-Party and Agent Management",
  "current_version": "1.0",
  "lifecycle_state": "draft",
  "versions": [
    {
      "version": "1.0",
      "created_at": "2024-01-15T10:00:00",
      "created_by": "system",
      "changes": "Initial version from control.yaml"
    }
  ]
}
```

---

## Operations

### Load Registry
```python
from level2.registry import ControlRegistry
registry = ControlRegistry("level1/controls.yaml")
```

### Update Lifecycle
```python
registry.set_lifecycle("SCF-001", "approved")
```

### Search by Domain
```python
controls = registry.get_by_domain("Access Control")
```

### Export Registry
```python
registry.export_registry("controls/registry_level2.json")
```

---

## Files Generated

```
controls/
└── registry_level2.json    ← Full control registry with versions
```

---

**Source**: `level1/controls.yaml`  
**Manages**: Control versioning, lifecycle, metadata  
**Next Step**: Level 3 (Policy Generation)
