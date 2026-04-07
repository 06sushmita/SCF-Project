# 📋 Controls Registry - Data Persistence

This folder stores the **master control registry** - the single source of truth for all compliance controls with their complete version history and metadata.

---

## 📂 Files & Importance

### 🔴 **CRITICAL** (Must Exist & Work)

#### **controls_registry.json** | Importance: 🌟🌟🌟🌟🌟
- **Purpose**: Master registry - stores ALL controls with complete version history
- **Format**: JSON array of control objects
- **Size**: Grows as controls are added/versioned (currently ~50KB for 20+ controls × versions)
- **Structure**:
  ```json
  [
    {
      "id": "SCF-001",
      "title": "Broker Registration Verification",
      "domain": "Access Control",
      "type": "Preventive",
      "versions": [
        {
          "version": "1.0",
          "statement": "...",
          "created": "2025-01-15T10:30:00Z",
          "created_by": "system",
          "status": "active",
          "audit_trail": [...]
        },
        {
          "version": "1.1",
          "statement": "...",
          "created": "2025-01-20T14:22:00Z",
          "created_by": "user@example.com",
          "status": "active",
          "reason_for_change": "Clarified broker categories"
        }
      ]
    }
  ]
  ```
- **Key Properties**:
  - `id` – Unique control identifier (SCF-NNN)
  - `title` – Human-readable control name
  - `domain` – Classification (8 possible domains)
  - `type` – Preventive/Detective/Corrective
  - `versions` – Array of all versions (immutable history)
  - `status` – draft/active/deprecated/archived
- **Modified By**: 
  - `RegistryAgent` (versioning, lifecycle)
  - API PATCH/POST endpoints
- **Read By**:
  - `RegistryAgent` (search, filter, retrieve)
  - API GET endpoints
  - PolicyAgent (fetch control for policy generation)
- **Critical for**:
  - **Compliance audits** (complete history of what changed, when, who)
  - **Traceability** (track control evolution)
  - **Search** (find controls by keyword, domain, type)
  - **Versioning** (support multiple versions of same control)
- **Backup**: Should be backed up and version-controlled
- **Constraints**:
  - Never delete records (append only)
  - Version numbers are immutable
  - Status changes are recorded in audit trail

---

## 🔄 Registry Lifecycle

```
CREATE: New control added
  ↓ (stored in controls_registry.json with version 1.0, status=draft)
UPDATE: Modify statement/objectives
  ↓ (new version 1.1 appended, old version preserved)
ACTIVATE: Move to active status
  ↓ (status field updated, audit trail recorded)
DEPRECATE: Mark as no longer applicable
  ↓ (status=deprecated, timestamp recorded)
ARCHIVE: Remove from active use
  ↓ (status=archived, but record preserved for audits)
```

---

## 🔗 Related Files

| File | Relationship |
|------|--------------|
| [../agents/registry.py](../agents/registry.py) | Manages read/write operations on controls_registry.json |
| [../api/main.py](../api/main.py) | Exposes this data via REST API endpoints |
| [../policies/](../policies/) | PolicyAgent reads from this registry to generate policies |

---

## 📊 Quick Stats

- **Current Controls**: See `controls_registry.json` for live count
- **Total Versions**: Sum of all version arrays across all controls
- **Audit Entries**: One per status change or update
- **Update Frequency**: Depends on regulation changes and policy updates

---

## ⚠️ Important Notes

- **Format**: Always JSON (not YAML; JSON is stricter)
- **Encoding**: UTF-8
- **Immutability**: Once written, versions never change (only new versions added)
- **Backup Strategy**: Keep git history; consider nightly snapshots for production
- **Size Limit**: No hard limit, but performance degrades >10MB (split into multiple files if needed)
