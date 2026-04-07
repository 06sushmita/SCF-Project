# 🔧 LEVEL 3 - Policy-as-Code

## Overview

**Level 3** converts controls into executable enforcement policies.

- **Source of Truth**: `level1/controls.yaml`
- **Output**: OPA/Rego policies + Python validators + test cases
- **Deliverable**: Complete policy packages (policy.rego + tests + metadata)

---

## How to Use

### Generate Policies

```bash
cd level3
python generator.py
```

### Output

```
🔧 GENERATING POLICIES FROM level1/controls.yaml
========================================

✓ SCF-001-v1-0: level3/policies/SCF-001-v1-0
✓ SCF-002-v1-0: level3/policies/SCF-002-v1-0
✓ SCF-003-v1-0: level3/policies/SCF-003-v1-0
...

✅ Generated 5 policy packages
Location: level3/policies/
```

---

## Policy Package Structure

Each control generates a complete policy package:

```
level3/policies/
└── SCF-001-v1-0/
    ├── policy.rego                ← OPA/Rego policy
    ├── positive_test.json         ← Compliant scenario
    ├── negative_test.json         ← Violation scenario
    └── control_reference.json     ← Control metadata
```

---

## File Descriptions

### policy.rego
**OPA/Rego policy** that enforces the control

```rego
package scf.scf_001

import future.keywords

allow if {
    input.context != null
    input.context.actor_type != null
    is_authorized
}

deny if {
    not allow
}

is_authorized if {
    input.context.metadata.authorized == true
}
```

### positive_test.json
**Compliant scenario** (should PASS)

```json
{
  "test_id": "SCF-001-pass",
  "test_name": "Compliant: Procedure For Enrollment...",
  "context": {
    "actor_type": "authorized_user",
    "metadata": {"authorized": true}
  },
  "expected": "PASS"
}
```

### negative_test.json
**Violation scenario** (should FAIL)

```json
{
  "test_id": "SCF-001-fail",
  "test_name": "Violation: Procedure For Enrollment...",
  "context": {
    "actor_type": "unauthorized_user",
    "metadata": {"authorized": false}
  },
  "expected": "FAIL"
}
```

### control_reference.json
**Control metadata** from control.yaml

```json
{
  "control_id": "SCF-001",
  "title": "Procedure For Enrollment / Registration Of Brokers",
  "statement": "Procedure for enrollment / registration...",
  "objective": "Ensure only authorised and verified parties...",
  "generated_at": "2026-03-30T17:00:00Z"
}
```

---

## Key Features

✅ **Reads from control.yaml** – Single source of truth  
✅ **Auto-generates Rego policies** – No manual coding needed  
✅ **Test cases included** – Positive + negative scenarios  
✅ **Control reference** – Links back to original control  
✅ **Deterministic** – Pass/fail results are consistent  

---

## How Policies Map to Controls

| Control Element | Policy Implementation |
|---|---|
| **Title** | Package name & comments |
| **Statement** | allows/denies rules |
| **Objective** | Policy logic enforcement |
| **Domain** | Policy package organization |

---

## Example: SCF-001 Policy

**Control Statement** (from control.yaml):
> "Brokers must submit enrollment requests on formal letterhead and receive unique code"

**Generated Policy** (policy.rego):
```rego
allow if {
    input.context.actor_type == "broker"
    input.metadata.enrollment_letter == true
    input.metadata.broker_code in data.registered_brokers
}
```

**Test Cases**:
- ✅ **Pass**: Actor=broker, letter=true, code=registered
- ❌ **Fail**: Actor=broker, letter=false, code=registered

---

## Execution Results

Each policy package can be tested:

```bash
cd level3/policies/SCF-001-v1-0
python ../evaluator.py .
```

Output:
```json
{
  "test_id": "SCF-001-pass",
  "result": "PASS",
  "compliance_score": 100.0
}
```

---

## Files Generated

```
level3/
├── generator.py              ← Policy generator
├── README.md                 ← This file
└── policies/
    ├── SCF-001-v1-0/        ← Policy package
    ├── SCF-002-v1-0/
    ├── SCF-003-v1-0/
    └── ...
```

---

**Source**: `level1/controls.yaml`  
**Transforms**: Controls → Policies (Rego + tests)  
**Ensures**: Deterministic, testable compliance logic  

---

## Next Steps

1. ✅ Run `python generator.py` to generate all policies
2. ✅ Navigate to `level3/policies/` to explore policy packages
3. ✅ Read policy READMEs for control-specific details
4. ✅ Run evaluators to validate policies
