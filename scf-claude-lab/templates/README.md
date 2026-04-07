# 📋 Templates - Boilerplate & Configuration

This folder contains **template files** used as blueprints for generating new controls, schemas, and metadata.

---

## 📂 Files & Importance

### 🟡 **IMPORTANT** (Generation & Consistency)

#### **control.yaml** | Importance: 🌟🌟🌟
- **Purpose**: Template for creating new control definitions
- **Format**: YAML
- **Usage**: Copy this template when adding a new control manually
- **Contains**:
  - Basic control fields (id, title, domain, type)
  - Control objectives
  - Control statements
  - Evidence requirements
  - Metadata fields
- **Used By**: 
  - ControlAgent (generates fills this template)
  - Manual control creation workflows
  - Documentation examples
- **Example Structure**:
  ```yaml
  id: SCF-NNN
  title: Control Title Here
  domain: [Access Control | Data Protection | etc]
  type: [Preventive | Detective | Corrective]
  objective: |
    Clearly state what this control achieves
  statement: |
    Describe how the control works
  evidence:
    - Type of evidence needed
    - Documentation required
  metadata:
    version: "1.0"
    created_date: 2025-01-15
    created_by: system
  ```

---

#### **schema.json** | Importance: 🌟🌟
- **Purpose**: Template for JSON schema definitions
- **Format**: JSON Schema (draft 7)
- **Usage**: Copy when defining new validation schemas
- **Contains**: Standard JSON Schema structure with annotations
- **Used By**: Schema generation scripts

---

#### **inheritance.yaml** | Importance: 🌟🌟
- **Purpose**: Template for control inheritance relationships
- **Format**: YAML
- **Usage**: Defines parent-child control relationships (for control hierarchies)
- **Example**:
  ```yaml
  parent_control: SCF-001
  child_controls:
    - SCF-001-A  # Sub-control A
    - SCF-001-B  # Sub-control B
  inheritance_type: [specialization | composition]
  ```

---

#### **lifecycle_note.md** | Importance: 🌟
- **Purpose**: Template for control lifecycle transition notes
- **Format**: Markdown
- **Usage**: Template for documenting why controls change status
- **Contains**:
  - Transition reason
  - Approver information
  - Effective date
  - Impact analysis
- **Example**:
  ```markdown
  # Lifecycle Change: SCF-001 (v1.0 → v1.1)
  
  **Transition**: Active → Superseded
  **Reason**: ....
  **Effective Date**: 2025-01-20
  **Approver**: Compliance Lead
  **Impact**: 5 dependent controls affected
  ```

---

## 🔗 Related Files

| File | Uses Templates From |
|------|---------------------|
| [../agents/control.py](../agents/control.py) | `control.yaml` for generation |
| [../controls/controls_registry.json](../controls/controls_registry.json) | Output uses `control.yaml` structure |
| [../schemas/](../schemas/) | Uses `schema.json` as reference |

---

## 🚀 Using Templates

### **To Create New Control**:
```bash
# Copy template
cp templates/control.yaml my_new_control.yaml

# Edit your_new_control.yaml
# (Fill in control fields)

# Add to registry via API
curl -X POST http://localhost:8000/api/v1/controls \
  -F "file=@my_new_control.yaml"
```

### **To Define New JSON Schema**:
```bash
# Copy template
cp templates/schema.json my_new_schema.json

# Edit my_new_schema.json
# (Add your properties, validation rules)
```
