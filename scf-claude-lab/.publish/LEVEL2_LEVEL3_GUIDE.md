# 📊 LEVEL 2 & LEVEL 3 - Integration Guide

## Complete Flow

```
level1/controls.yaml (Single Source of Truth)
        ↓
    [LEVEL 2]
    Control Registry
    - Versioning
    - Lifecycle management
    - Searchable registry
        ↓
    controls/registry_level2.json
        ↓
    [LEVEL 3]
    Policy Generator
    - Rego policies
    - Test cases
    - Metadata
        ↓
    level3/policies/SCF-XXX-v1-0/
    - policy.rego
    - positive_test.json
    - negative_test.json
    - control_reference.json
```

---

## Project Structure

```
scf-claude-lab/
│
├── level1/                    EXTRACTION & SOURCE
│   ├── controls.yaml          📌 SINGLE SOURCE OF TRUTH
│   ├── generate.py
│   └── risk.json
│
├── level2/                    ✅ REGISTRY & VERSIONING
│   ├── registry.py            Control registry manager
│   └── README.md              Documentation
│
├── level3/                    ✅ POLICY GENERATION
│   ├── generator.py           Policy generator
│   ├── README.md              Documentation
│   └── policies/              Generated policy packages
│       ├── SCF-001-v1-0/
│       ├── SCF-002-v1-0/
│       └── ...
│
├── controls/
│   └── registry_level2.json   Generated registry
│
├── api/                       REST API layer
├── agents/                    Core engines
└── docs/                      Documentation hub
```

---

## Usage: Step by Step

### Step 1: Load Level 2 Registry

```bash
cd level2
python registry.py
```

**What it does**:
- ✅ Reads `level1/controls.yaml`
- ✅ Creates control registry with versions
- ✅ Sets lifecycle states (draft, approved, active)
- ✅ Exports to `controls/registry_level2.json`

**Output**:
```
📖 LOADING 9 CONTROLS FROM level1/controls.yaml
✅ Total Controls: 9

📊 BY DOMAIN:
  • Access Control: 9

✓ Registry exported to controls/registry_level2.json
```

---

### Step 2: Generate Level 3 Policies

```bash
cd level3
python generator.py
```

**What it does**:
- ✅ Reads `level1/controls.yaml` (same source!)
- ✅ Generates OPA/Rego policies
- ✅ Creates test cases (positive + negative)
- ✅ Stores control metadata
- ✅ Outputs complete policy packages

**Output**:
```
🔧 GENERATING POLICIES FROM level1/controls.yaml

✓ SCF-001-v1-0: level3/policies/SCF-001-v1-0
✓ SCF-002-v1-0: level3/policies/SCF-002-v1-0
✓ SCF-003-v1-0: level3/policies/SCF-003-v1-0

✅ Generated 5 policy packages
Location: level3/policies/
```

---

## Control Data Flow Example

### Input (from control.yaml)

```yaml
- control_id: SCF-001
  title: Procedure For Enrollment / Registration Of Brokers
  control_statement: Procedure for enrollment / registration of brokers 
    Receiving Offices may follow a simple procedure for enrolment/registration 
    of brokers.
  objective: Ensure only authorised and verified parties are permitted
  control_type: Preventive
  control_domain: Access Control
  control_family: Third-Party and Agent Management
```

### Level 2: Registry Entry

```json
{
  "control_id": "SCF-001",
  "title": "Procedure For Enrollment / Registration Of Brokers",
  "control_statement": "Procedure for enrollment / registration...",
  "control_type": "Preventive",
  "control_domain": "Access Control",
  "current_version": "1.0",
  "lifecycle_state": "approved",
  "versions": [
    {
      "version": "1.0",
      "created_at": "2026-03-30T17:00:00Z",
      "created_by": "system",
      "changes": "Initial version from control.yaml"
    }
  ]
}
```

### Level 3: Generated Policy

**policy.rego**:
```rego
package scf.scf_001

# SCF-001: Procedure For Enrollment / Registration Of Brokers
# Type: Preventive | Domain: Access Control

allow if {
    input.context != null
    input.context.actor_type != null
    is_authorized
}

is_authorized if {
    input.context.metadata.authorized == true
}
```

**Test Cases**:
```json
{
  "positive_test": {
    "actor_type": "authorized_user",
    "authorized": true,
    "expected": "PASS",
    "statement": "Ensure only authorised and verified parties..."
  },
  "negative_test": {
    "actor_type": "unauthorized_user",
    "authorized": false,
    "expected": "FAIL",
    "statement": "Ensure only authorised and verified parties..."
  }
}
```

---

## Key Principles

### ✅ Single Source of Truth
- All controls defined in `level1/controls.yaml`
- Level 2 reads from it
- Level 3 reads from it
- No duplication, no inconsistency

### ✅ Versioning
- Level 2 tracks versions (1.0 → 1.1 → 2.0)
- Each version immutable
- Full audit trail

### ✅ Lifecycle Management
- draft → approved → active → deprecated
- Clear state transitions
- Tracked in registry

### ✅ Policy Automation
- Control statements → Rego policies
- Automatic test case generation
- Deterministic pass/fail results

### ✅ Traceability
- Every policy links to source control
- Control reference metadata included
- Full control statement preserved

---

## Generated Files

### Controls Directory
```
controls/
└── registry_level2.json      ← Complete registry with versions
```

### Level 3 Policies
```
level3/policies/
├── SCF-001-v1-0/
│   ├── policy.rego           ← OPA/Rego policy
│   ├── positive_test.json    ← Valid scenario
│   ├── negative_test.json    ← Invalid scenario
│   └── control_reference.json ← Metadata
├── SCF-002-v1-0/
├── SCF-003-v1-0/
└── ...
```

---

## Running Commands

### Level 2 Only
```bash
cd level2 && python registry.py
```

### Level 3 Only
```bash
cd level3 && python generator.py
```

### Both (Complete Workflow)
```bash
# Terminal 1: Level 2
cd level2 && python registry.py

# Terminal 2: Level 3
cd level3 && python generator.py

# View results
ls -la controls/registry_level2.json
ls -la level3/policies/
```

---

## Verification Checklist

✅ `level1/controls.yaml` exists and has controls  
✅ `level2/registry.py` reads from controls.yaml  
✅ `level3/generator.py` reads from controls.yaml  
✅ Registry exports to `controls/registry_level2.json`  
✅ Policies generate to `level3/policies/`  
✅ Each policy has: .rego + tests + metadata  
✅ No control statements hardcoded (all from YAML)  
✅ Lifecycle states properly tracked  

---

## Troubleshooting

### Registry not loading
```bash
# Check control.yaml path
ls -la level1/controls.yaml

# Check YAML is valid
python -c "import yaml; yaml.safe_load(open('level1/controls.yaml'))"
```

### Policies not generating
```bash
# Check generator reads YAML
cd level3
python -c "from generator import PolicyGenerator; print(PolicyGenerator().controls)"
```

### Missing files
```bash
# Verify structure
find . -name "registry.py" -o -name "generator.py" -o -name "controls.yaml"
```

---

## Next Steps

1. ✅ Verify `level1/controls.yaml` exists
2. ✅ Run Level 2: `cd level2 && python registry.py`
3. ✅ Run Level 3: `cd level3 && python generator.py`
4. ✅ Check outputs in `controls/` and `level3/policies/`
5. ✅ Read policy READMEs for details
6. ✅ Integrate with API for full compliance engine

---

**Status**: ✅ Complete  
**Source of Truth**: `level1/controls.yaml`  
**Registry**: Level 2 manages versions & lifecycle  
**Policies**: Level 3 generates executable enforcement logic
